"""
Flask API Routes - نقاط النهاية الرئيسية
"""

from flask import Flask, request, jsonify, g
from flask_cors import CORS
import psycopg
from psycopg.rows import dict_row
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from core.config import Config

from blockchain.chain import Blockchain
from services.audit_service import AuditService
from services.receipt_service import ReceiptService
from .admin_candidates import admin_candidates_bp
import io
import csv
from flask import Response, send_from_directory

# تحميل المتغيرات البيئية
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://evotingdz.live", "https://www.evotingdz.live", "http://209.38.44.237:3000"]}})

# ==================== Database Connection ====================

def get_db():
    """إنشاء اتصال بقاعدة البيانات"""
    if 'db' not in g:
        g.db = psycopg.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 5432)),
            dbname=os.getenv('DB_NAME', 'voting_system'),
            user=os.getenv('DB_USER', 'voting_admin'),
            password=os.getenv('DB_PASSWORD'),
            row_factory=dict_row
        )
    return g.db

@app.teardown_appcontext
def close_db(error):
    """إغلاق الاتصال عند انتهاء الطلب"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# تهيئة البلوكشين مرة واحدة فقط عند إقلاع الخادم
_blockchain_instance = None

def get_blockchain():
    """الحصول على نسخة البلوكشين الوحيدة"""
    global _blockchain_instance
    if _blockchain_instance is None:
        # اتصال مخصص للبلوكشين (لا يُغلق مع كل طلب)
        bc_db = psycopg.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 5432)),
            dbname=os.getenv('DB_NAME', 'voting_system'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD'),
            autocommit=False,
            row_factory=dict_row
        )
        _blockchain_instance = Blockchain(bc_db)
    return _blockchain_instance

# ==================== Root ====================

@app.route('/', methods=['GET'])
def root():
    """الصفحة الرئيسية"""
    return jsonify({
        'name': 'نظام التصويت الرقمي الجزائري / Système de Vote Numérique Algérien',
        'version': '2.0',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'candidates': '/api/candidates',
            'voter_status': '/api/voter-status/<nfc_uid>',
            'vote': '/api/vote (POST)',
            'verify_chain': '/api/verify-chain',
            'stats': '/api/stats',
        }
    })

app.register_blueprint(admin_candidates_bp, url_prefix='/api/admin/candidates')

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    """تقديم الملفات المرفوعة (صور المرشحين)"""
    return send_from_directory(
        '/opt/algerian-voting-system/uploads',
        filename,
        max_age=3600
    )

# ==================== Authentication ====================

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """تسجيل دخول المشرف بـ username + password باستخدام bcrypt"""
    import bcrypt, secrets
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({'error': 'بيانات ناقصة / Missing credentials'}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT admin_id, username, password_hash, is_active FROM admin_users WHERE username=%s",
        (username,)
    )
    row = cursor.fetchone()

    if row and row['is_active']:
        pw_hash = row['password_hash'].encode() if isinstance(row['password_hash'], str) else row['password_hash']
        if bcrypt.checkpw(password.encode('utf-8'), pw_hash):
            token = secrets.token_hex(32)
            
            # حفظ الجلسة في قاعدة البيانات
            expires_at = datetime.now() + timedelta(hours=Config.SESSION_EXPIRY_HOURS)
            cursor.execute(
                "INSERT INTO admin_sessions (admin_id, token, expires_at) VALUES (%s, %s, %s)",
                (row['admin_id'], token, expires_at)
            )
            db.commit()
            
            AuditService.log('ADMIN_LOGIN_SUCCESS', 'SUCCESS', None)
            return jsonify({
                'success': True,
                'token': token,
                'username': username,
                'expires_in': Config.SESSION_EXPIRY_HOURS * 3600
            })

    AuditService.log('ADMIN_LOGIN_FAILED', 'FAILED', None, 'Invalid credentials')
    return jsonify({'error': 'بيانات خاطئة / Invalid credentials'}), 401

# ==================== Voter Endpoints ====================

@app.route('/api/voter-status/<nfc_uid>', methods=['GET'])
def check_voter_status(nfc_uid):
    """
    التحقق من حالة الناخب
    
    Returns: {eligible, has_voted, name_ar, name_fr}
    """
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute(
            "SELECT voter_id, nfc_uid, full_name_ar, full_name_fr, has_voted FROM voters WHERE nfc_uid=%s",
            (nfc_uid,)
        )
        result = cursor.fetchone()
    finally:
        cursor.close()
    
    if not result:
        AuditService.log('VOTER_NOT_FOUND', 'FAILED', nfc_uid, 'Not found')
        return jsonify({
            'error': 'بطاقة غير مسجلة / Carte non enregistrée'
        }), 404
    
    has_voted = result['has_voted']
    AuditService.log('VOTER_AUTHENTICATED', 'SUCCESS', nfc_uid)
    
    return jsonify({
        'eligible': not has_voted,
        'message': 'صوّت مسبقاً / Déjà voté' if has_voted else 'مؤهل للتصويت / Éligible',
        'name_ar': result['full_name_ar'] or '',
        'name_fr': result['full_name_fr'] or '',
        'has_voted': has_voted
    })

# ==================== Candidate Endpoints ====================

@app.route('/api/candidates', methods=['GET'])
def get_candidates():
    """
    الحصول على قائمة المرشحين
    
    Returns: [{candidate_id, full_name_ar, full_name_fr, ...}]
    """
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT 
            candidate_id,
            full_name_ar,
            full_name_fr,
            party_name_ar,
            party_name_fr,
            photo_url,
            display_order
        FROM candidates
        WHERE is_active = TRUE
        ORDER BY display_order ASC
    """)
    
    candidates = cursor.fetchall()
    cursor.close()
    
    return jsonify(candidates)

# ==================== Voting Endpoints ====================

@app.route('/api/vote', methods=['POST'])
def cast_vote():
    """
    استقبال صوت جديد
    
    Body: {"nfc_uid": "...", "candidate_id": 3}
    """
    import psycopg
    data = request.get_json(silent=True) or {}
    nfc_uid = data.get('nfc_uid') or data.get('voter_uid')
    candidate_id = data.get('candidate_id')
    
    # التحقق من البيانات
    if not nfc_uid or not candidate_id:
        return jsonify({'error': 'Missing required fields'}), 400
    
    db = get_db()
    
    try:
        cursor = db.cursor()
        
        # 1. جلب الناخب مع LOCK (يمنع race condition)
        # Select voter properties FOR UPDATE within transaction
        cursor.execute("SELECT voter_id, has_voted, voted_at FROM voters WHERE nfc_uid = %s FOR UPDATE", (nfc_uid,))
        voter = cursor.fetchone()
        
        if not voter:
            AuditService.log('VOTER_NOT_FOUND', 'FAILED', nfc_uid, 'Not found')
            return jsonify({'error': 'Voter not found', 'code': 'VOTER_NOT_FOUND'}), 404
            
        # 2. فحص has_voted (الحماية الأولى)
        if voter['has_voted']:
            AuditService.log('VOTE_DUPLICATE_BLOCKED', 'WARNING', nfc_uid, 'Already voted')
            voted_at_iso = voter['voted_at'].isoformat() if voter.get('voted_at') else None
            return jsonify({
                'error': 'This voter has already voted',
                'error_ar': 'هذا الناخب قد صوّت مسبقاً',
                'error_fr': 'Cet électeur a déjà voté',
                'code': 'ALREADY_VOTED',
                'voted_at': voted_at_iso
            }), 403
            
        # 3. التحقق: هل المرشح موجود؟
        cursor.execute("SELECT candidate_id FROM candidates WHERE candidate_id = %s AND is_active = TRUE", 
                       (candidate_id,))
        if not cursor.fetchone():
            AuditService.log('SYSTEM_ERROR', 'FAILED', nfc_uid, 'Invalid candidate')
            return jsonify({'error': 'مرشح غير صالح / Invalid candidate'}), 400
        
        # 4. إنشاء Vote record (الحماية الثالثة من خلال DB UNIQUE constraint)
        cursor.execute("INSERT INTO votes (voter_id, candidate_id) VALUES (%s, %s) RETURNING id", (voter['voter_id'], candidate_id))
        vote_id = cursor.fetchone()['id']
        
        # 5. إضافة الصوت للبلوكشين (بدون الـ commit الداخلي)
        vote_hash = get_blockchain().add_vote(
            {'candidate_id': candidate_id, 'nfc_uid': nfc_uid},
            os.getenv('PUBLIC_KEY_PATH', '../secure/public_key.pem'),
            commit=False
        )
        
        # 6. تحديث حالة الناخب (الحماية الثانية)
        cursor.execute("""
            UPDATE voters 
            SET has_voted = TRUE, voted_at = NOW() 
            WHERE nfc_uid = %s
        """, (nfc_uid,))
        
        # 7. commit كوحدة واحدة (atomicity)
        db.commit()
        
        # 8. generating receipt AFTER successful commit 
        # But wait, ReceiptService.generate_receipt() opens a transaction but we want it stored. Let's do it right.
        # Actually generate_receipt does standard DB operations without explicitly committing or it does?
        # Oh, ReceiptService has cursor.close(), no commit. Wait, that means standard auto-commit unless we are in a transaction.
        # Better just use the ReceiptService normally (it fetches a connection and inserts, so it will commit if auto).
        block_index = len(get_blockchain()) - 1
        receipt = ReceiptService.generate_receipt(vote_hash, vote_hash, block_index, election_id=1)
        
        # 9. تسجيل في Audit Log
        AuditService.log('VOTE_CAST', 'SUCCESS', nfc_uid)
        AuditService.log('RECEIPT_GENERATED', 'SUCCESS', nfc_uid)
        
        cursor.close()
        
        return jsonify({
            'success': True,
            'message': 'Vote recorded successfully',
            'vote_id': vote_id,
            'block_hash': vote_hash,
            'message_ar': 'تم التصويت بنجاح',
            'message_fr': 'Votre vote a été enregistré',
            'timestamp': datetime.now().isoformat(),
            'receipt': receipt
        }), 200
        
    except psycopg.IntegrityError as e:
        db.rollback()
        return jsonify({
            'error': 'Duplicate vote detected',
            'code': 'DUPLICATE_VOTE'
        }), 409
    except Exception as e:
        db.rollback()
        AuditService.log('SYSTEM_ERROR', 'FAILED', nfc_uid, str(e))
        
        return jsonify({
            'error': 'فشل في حفظ الصوت / Failed to save vote',
            'details': str(e)
        }), 500

# ==================== Blockchain Endpoints ====================

@app.route('/api/verify-chain', methods=['GET'])
def verify_chain():
    """التحقق من سلامة البلوكشين"""
    is_valid, message = get_blockchain().verify_integrity()
    
    if is_valid:
        AuditService.log('BLOCKCHAIN_VERIFIED', 'SUCCESS', None)
    
    return jsonify({
        'valid': is_valid,
        'message': message,
        'chain_length': len(get_blockchain()),
        'last_block_hash': get_blockchain().chain[-1].hash if len(get_blockchain()) > 0 else None
    })

@app.route('/api/blockchain/status', methods=['GET'])
def blockchain_status():
    """معلومات عن حالة البلوكشين"""
    return jsonify({
        'total_blocks': len(get_blockchain()),
        'total_votes': len(get_blockchain()) - 1,  # exclude genesis
        'last_block': get_blockchain().chain[-1].to_dict() if len(get_blockchain()) > 0 else None
    })

# ==================== Statistics Endpoints ====================

@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """إحصائيات التصويت الحية"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT COUNT(*) as total, COUNT(*) FILTER (WHERE has_voted = TRUE) as voted, MAX(voted_at) as last_vote FROM voters")
        row = cursor.fetchone()
        
        total_voters = row['total'] if row and row['total'] else 0
        voted_count = row['voted'] if row and row['voted'] else 0
        remaining_count = total_voters - voted_count
        turnout_percentage = round((voted_count / total_voters * 100), 2) if total_voters > 0 else 0
        
        cursor.execute("SELECT * FROM elections WHERE id = 1")
        election = cursor.fetchone() or {}
        
        status = election.get('status', 'OPEN')
        results_status = 'PRELIMINARY' if status == 'OPEN' else 'OFFICIAL'
        
        cursor.execute("""
            SELECT c.candidate_id, c.full_name_ar, c.full_name_fr, COUNT(v.id) as vote_count
            FROM candidates c
            LEFT JOIN votes v ON c.candidate_id = v.candidate_id
            GROUP BY c.candidate_id, c.full_name_ar, c.full_name_fr
            ORDER BY c.candidate_id ASC
        """)
        candidates_rows = cursor.fetchall()
        
        candidates_stats = []
        colors = ['#006233', '#D21034', '#C9A961', '#1A73E8', '#F9AB00']
        for idx, c in enumerate(candidates_rows):
            c_votes = c['vote_count']
            c_pct = round((c_votes / voted_count * 100), 2) if voted_count > 0 else 0
            candidates_stats.append({
                'id': c['candidate_id'],
                'name_ar': c['full_name_ar'],
                'name_fr': c['full_name_fr'],
                'votes': c_votes,
                'percentage': c_pct,
                'color': colors[idx % len(colors)]
            })
        
        chain_len = len(get_blockchain())
        last_vote_time = row['last_vote'].isoformat() if row and row['last_vote'] else None
            
        return jsonify({
            'total_voters': total_voters,
            'voted_count': voted_count,
            'remaining_count': remaining_count,
            'remaining': remaining_count,
            'turnout_percentage': turnout_percentage,
            'blockchain_length': chain_len,
            'candidates': candidates_stats,
            'last_updated': datetime.now().isoformat(),
            'last_vote_time': last_vote_time,
            'election': {
                'name_ar': election.get('name_ar', 'الانتخابات الرئاسية'),
                'name_fr': election.get('name_fr', 'Élection Présidentielle'),
                'end_date': election['end_date'].isoformat() if election.get('end_date') else None
            },
            'results_status': results_status,
            'message_ar': "نتائج أولية — تحدّث لحظياً",
            'message_fr': "Résultats préliminaires — mis à jour en temps réel"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()

@app.route('/api/stats/wilaya', methods=['GET'])
def get_wilaya_stats():
    """إحصائيات حسب الولاية"""
    # TODO: إضافة تحقق من Token المشرف
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT 
                wilaya, 
                COUNT(*) as total_voters, 
                COUNT(*) FILTER (WHERE has_voted = TRUE) as voted_count
            FROM voters
            GROUP BY wilaya
            ORDER BY total_voters DESC
        """)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            t = row['total_voters'] or 0
            v = row['voted_count'] or 0
            pct = (v / t * 100) if t > 0 else 0
            results.append({
                'wilaya': row['wilaya'],
                'total_voters': t,
                'voted_count': v,
                'turnout_pct': pct
            })
            
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()

# ==================== Decryption Endpoint ====================

@app.route('/api/decrypt-votes', methods=['POST'])
def decrypt_votes():
    """
    فك تشفير جميع الأصوات (للمشرفين فقط)
    
    Body: {"private_key_password": "..."}
    """
    # TODO: إضافة تحقق من Token المشرف
    
    data = request.json
    password = data.get('private_key_password')
    
    if not password:
        return jsonify({'error': 'Password required'}), 400
    
    try:
        # فك التشفير
        blockchain = get_blockchain()
        
        # التحقق من سلامة البلوكشين
        integrity_valid, integrity_msg = blockchain.verify_integrity()
        
        votes = blockchain.decrypt_all_votes(
            os.getenv('PRIVATE_KEY_PATH', '../secure/private_key_encrypted.pem'),
            password
        )
        
        # حساب النتائج
        vote_counts = {}
        for vote in votes:
            cid = vote['candidate_id']
            vote_counts[cid] = vote_counts.get(cid, 0) + 1
        
        # جلب جميع المرشحين
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT candidate_id, full_name_ar, full_name_fr FROM candidates ORDER BY candidate_id")
        candidates_rows = cursor.fetchall()
        cursor.close()
        
        # دمج النتائج بتنسيق قائمة (List) كما يتوقعه الـ Frontend
        results_list = []
        total_votes = len(votes)
        colors = ['#006233', '#D21034', '#C9A961', '#1A73E8', '#F9AB00']
        
        for idx, row in enumerate(candidates_rows):
            cid = row['candidate_id']
            count = vote_counts.get(cid, 0)
            results_list.append({
                'candidate_id': cid,
                'name_ar': row['full_name_ar'],
                'name_fr': row['full_name_fr'],
                'votes': count,
                'percentage': (count / total_votes * 100) if total_votes > 0 else 0,
                'color': colors[idx % len(colors)]
            })
            
        # ترتيب النتائج من الأعلى للأدنى
        results_list.sort(key=lambda x: x['votes'], reverse=True)
        
        AuditService.log('ELECTION_DECRYPTED', 'SUCCESS', None, f"Total votes: {total_votes}")
        
        return jsonify({
            'success': True,
            'total_votes': total_votes,
            'results': results_list,
            'blockchain_integrity': integrity_valid,
            'decrypted_at': datetime.now().isoformat()
        })
    
    except Exception as e:
        error_msg = str(e)
        error_ar = "فشل فك التشفير - تأكد من كلمة المرور"
        # Check for wrong password specific errors from cryptography
        if "padding" in error_msg.lower() or "decryption failed" in error_msg.lower():
            error_ar = "كلمة السر خاطئة - المفتاح غير متاح"
            error_msg = "Wrong password"
            
        AuditService.log('DECRYPTION_FAILED', 'FAILED', None, error_msg)
        return jsonify({
            'success': False,
            'error': 'فك التشفير فشل / Decryption failed',
            'error_ar': error_ar,
            'details': error_msg
        }), 400

# ==================== Missing Endpoints ====================

# ==================== Audit Endpoints ====================

@app.route('/api/audit/logs', methods=['GET'])
def get_audit_logs():
    # TODO: Add @require_admin guard
    action_type = request.args.get('action_type')
    status = request.args.get('status')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    result = AuditService.query(action_type, status, date_from, date_to, page, per_page)
    AuditService.log('AUDIT_VIEWED', 'SUCCESS', None)
    return jsonify(result)

@app.route('/api/audit/stats', methods=['GET'])
def get_audit_stats():
    # TODO: Add @require_admin guard
    stats = AuditService.get_stats()
    return jsonify(stats)

@app.route('/api/audit/export', methods=['GET'])
def export_audit_logs():
    # TODO: Add @require_admin guard
    action_type = request.args.get('action_type')
    status = request.args.get('status')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    csv_data = AuditService.export_csv(action_type, status, date_from, date_to)
    AuditService.log('AUDIT_EXPORTED', 'SUCCESS', None)
    
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=audit_export.csv"}
    )

# ==================== Receipt Verification ====================

@app.route('/api/verify/<receipt_code>', methods=['GET'])
def verify_receipt(receipt_code):
    result = ReceiptService.verify_receipt(receipt_code)
    if result.get('verified'):
        AuditService.log('RECEIPT_VERIFIED', 'SUCCESS', None)
    else:
        AuditService.log('RECEIPT_VERIFICATION_FAILED', 'FAILED', None)
    return jsonify(result)

@app.route('/api/blockchain/all', methods=['GET'])
def get_all_blocks():
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        chain = get_blockchain().chain
        total = len(chain)
        
        # apply offset and limit
        # Reverse order, latest blocks first
        reversed_chain = chain[::-1]
        paginated = reversed_chain[offset:offset+limit]
        
        blocks = []
        for b in paginated:
            blocks.append({
                'block_index': b.index,
                'timestamp': datetime.fromtimestamp(b.timestamp).isoformat() if isinstance(b.timestamp, float) else (b.timestamp.isoformat() if hasattr(b.timestamp, 'isoformat') else str(b.timestamp)),
                'encrypted_vote': b.encrypted_vote,
                'previous_hash': b.previous_hash,
                'current_hash': b.hash,
                'nonce': b.nonce
            })
            
        return jsonify({
            'blocks': blocks,
            'total': total,
            'limit': limit,
            'offset': offset
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== Health Check ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """فحص صحة النظام"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'blockchain_length': len(get_blockchain()),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
