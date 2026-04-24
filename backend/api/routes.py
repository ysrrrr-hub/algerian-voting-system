"""
Flask API Routes - نقاط النهاية الرئيسية
"""

from flask import Flask, request, jsonify, g
from flask_cors import CORS
import psycopg
from psycopg.rows import dict_row
from datetime import datetime
import os
from dotenv import load_dotenv

from blockchain.chain import Blockchain
from utils.audit import log_action

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
            autocommit=False
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
            log_action(db, 'ADMIN_LOGIN', None, request.remote_addr, True)
            return jsonify({
                'success': True,
                'token': token,
                'username': username,
                'expires_in': 3600
            })

    log_action(db, 'ADMIN_LOGIN', None, request.remote_addr, False, 'Invalid credentials')
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
        log_action(db, 'VOTER_CHECK', nfc_uid, request.remote_addr, False, 'Not found')
        return jsonify({
            'error': 'بطاقة غير مسجلة / Carte non enregistrée'
        }), 404
    
    has_voted = result['has_voted']
    log_action(db, 'VOTER_CHECK', nfc_uid, request.remote_addr, True)
    
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
    data = request.json
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
            log_action(db, 'VOTE_ATTEMPT', nfc_uid, request.remote_addr, False, 'Not found')
            return jsonify({'error': 'Voter not found', 'code': 'VOTER_NOT_FOUND'}), 404
            
        # 2. فحص has_voted (الحماية الأولى)
        if voter['has_voted']:
            log_action(db, 'VOTE_ATTEMPT', nfc_uid, request.remote_addr, False, 'Already voted')
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
            log_action(db, 'VOTE_ATTEMPT', nfc_uid, request.remote_addr, False, 'Invalid candidate')
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
        
        # 8. تسجيل في Audit Log
        log_action(db, 'VOTE_CAST', nfc_uid, request.remote_addr, True)
        
        cursor.close()
        
        return jsonify({
            'success': True,
            'message': 'Vote recorded successfully',
            'vote_id': vote_id,
            'block_hash': vote_hash,
            'message_ar': 'تم التصويت بنجاح',
            'message_fr': 'Vote enregistré avec succès',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except psycopg.IntegrityError as e:
        db.rollback()
        return jsonify({
            'error': 'Duplicate vote detected',
            'code': 'DUPLICATE_VOTE'
        }), 409
    except Exception as e:
        db.rollback()
        log_action(db, 'VOTE_ATTEMPT', nfc_uid, request.remote_addr, False, str(e))
        
        return jsonify({
            'error': 'فشل في حفظ الصوت / Failed to save vote',
            'details': str(e)
        }), 500

# ==================== Blockchain Endpoints ====================

@app.route('/api/verify-chain', methods=['GET'])
def verify_chain():
    """التحقق من سلامة البلوكشين"""
    is_valid, message = get_blockchain().verify_integrity()
    
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
        
        cursor.execute("""
            SELECT c.candidate_id, c.full_name_ar, c.full_name_fr, COUNT(v.id) as vote_count
            FROM candidates c
            LEFT JOIN votes v ON c.candidate_id = v.candidate_id
            GROUP BY c.candidate_id, c.full_name_ar, c.full_name_fr
            ORDER BY c.candidate_id ASC
        """)
        candidates_rows = cursor.fetchall()
        
        candidates_stats = []
        for c in candidates_rows:
            c_votes = c['vote_count']
            c_pct = round((c_votes / voted_count * 100), 2) if voted_count > 0 else 0
            candidates_stats.append({
                'id': c['candidate_id'],
                'name_ar': c['full_name_ar'],
                'name_fr': c['full_name_fr'],
                'votes': c_votes,
                'percentage': c_pct
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
            'last_vote_time': last_vote_time
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
        votes = get_blockchain().decrypt_all_votes(
            os.getenv('PRIVATE_KEY_PATH', '../secure/private_key_encrypted.bin'),
            password
        )
        
        # حساب النتائج
        vote_counts = {}
        for vote in votes:
            cid = vote['candidate_id']
            vote_counts[cid] = vote_counts.get(cid, 0) + 1
        
        # جلب أسماء المرشحين
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT candidate_id, full_name_ar, full_name_fr FROM candidates")
        candidates = {row['candidate_id']: row for row in cursor.fetchall()}
        cursor.close()
        
        # دمج النتائج
        results = {}
        total_votes = len(votes)
        
        for cid, count in vote_counts.items():
            candidate = candidates.get(cid, {})
            results[cid] = {
                'candidate_id': cid,
                'name_ar': candidate.get('full_name_ar', 'Unknown'),
                'name_fr': candidate.get('full_name_fr', 'Unknown'),
                'votes': count,
                'percentage': (count / total_votes * 100) if total_votes > 0 else 0
            }
        
        log_action(db, 'DECRYPT_RESULTS', None, request.remote_addr, True)
        
        return jsonify({
            'success': True,
            'total_votes': total_votes,
            'results': results,
            'votes': votes  # التفاصيل الكاملة
        })
    
    except ValueError as e:
        log_action(db, 'DECRYPT_RESULTS', None, request.remote_addr, False, str(e))
        return jsonify({'error': 'فك التشفير فشل / Decryption failed', 'details': str(e)}), 400

# ==================== Missing Endpoints ====================

@app.route('/api/audit-log', methods=['GET'])
def get_audit_log():
    try:
        limit = int(request.args.get('limit', 200))
        offset = int(request.args.get('offset', 0))
        action_type = request.args.get('action_type')
        
        db = get_db()
        cursor = db.cursor()
        
        base_query = "FROM audit_log"
        params = []
        if action_type:
            base_query += " WHERE action_type = %s"
            params.append(action_type)
            
        cursor.execute(f"SELECT COUNT(*) as t {base_query}", tuple(params))
        total_row = cursor.fetchone()
        total = total_row['t'] if total_row else 0
        
        cursor.execute(f"SELECT log_id, action_type, nfc_uid, ip_address, success, error_message, timestamp {base_query} ORDER BY timestamp DESC LIMIT %s OFFSET %s", tuple(params + [limit, offset]))
        rows = cursor.fetchall()
        
        logs = []
        for r in rows:
            logs.append({
                'log_id': r['log_id'],
                'action_type': r['action_type'],
                'nfc_uid': r['nfc_uid'],
                'ip_address': r['ip_address'],
                'success': r['success'],
                'error_message': r['error_message'],
                'timestamp': r['timestamp'].isoformat() if r['timestamp'] else None
            })
            
        return jsonify({
            'logs': logs,
            'total': total,
            'limit': limit,
            'offset': offset
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()

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
