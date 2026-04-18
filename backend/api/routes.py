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
CORS(app, origins=os.getenv('ALLOWED_ORIGINS', '*').split(','))

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
    data = request.json or {}
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
    
    # استخدام الدالة المخزنة
    cursor.execute("SELECT * FROM check_voter_eligibility(%s)", (nfc_uid,))
    result = cursor.fetchone()
    cursor.close()
    
    if not result:
        log_action(db, 'VOTER_CHECK', nfc_uid, request.remote_addr, False, 'Not found')
        return jsonify({
            'error': 'بطاقة غير مسجلة / Carte non enregistrée'
        }), 404
    
    log_action(db, 'VOTER_CHECK', nfc_uid, request.remote_addr, True)
    
    return jsonify({
        'eligible': result['eligible'],
        'message': result['message'],
        'name_ar': result['voter_name_ar'],
        'name_fr': result['voter_name_fr'],
        'has_voted': not result['eligible']  # إذا غير مؤهل = صوّت أو غير مسجل
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
    data = request.json
    nfc_uid = data.get('nfc_uid')
    candidate_id = data.get('candidate_id')
    
    # التحقق من البيانات
    if not nfc_uid or not candidate_id:
        return jsonify({'error': 'Missing required fields'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    # 1. التحقق: هل الناخب مؤهل؟
    cursor.execute("SELECT * FROM check_voter_eligibility(%s)", (nfc_uid,))
    voter = cursor.fetchone()
    
    if not voter or not voter['eligible']:
        log_action(db, 'VOTE_ATTEMPT', nfc_uid, request.remote_addr, False, 
                   voter['message'] if voter else 'Not found')
        return jsonify({'error': voter['message'] if voter else 'Invalid voter'}), 403
    
    # 2. التحقق: هل المرشح موجود؟
    cursor.execute("SELECT candidate_id FROM candidates WHERE candidate_id = %s AND is_active = TRUE", 
                   (candidate_id,))
    if not cursor.fetchone():
        cursor.close()
        log_action(db, 'VOTE_ATTEMPT', nfc_uid, request.remote_addr, False, 'Invalid candidate')
        return jsonify({'error': 'مرشح غير صالح / Invalid candidate'}), 400
    
    try:
        # 3. إضافة الصوت للبلوكشين
        vote_hash = get_blockchain().add_vote(
            {'candidate_id': candidate_id, 'nfc_uid': nfc_uid},
            os.getenv('PUBLIC_KEY_PATH', '../secure/public_key.pem')
        )
        
        # 4. تحديث حالة الناخب
        cursor.execute("""
            UPDATE voters 
            SET has_voted = TRUE, voted_at = NOW() 
            WHERE nfc_uid = %s
        """, (nfc_uid,))
        
        db.commit()
        
        # 5. تسجيل في Audit Log
        log_action(db, 'VOTE_CAST', nfc_uid, request.remote_addr, True)
        
        cursor.close()
        
        return jsonify({
            'success': True,
            'vote_hash': vote_hash,
            'message_ar': 'تم التصويت بنجاح',
            'message_fr': 'Vote enregistré avec succès',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        db.rollback()
        cursor.close()
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
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT * FROM voting_statistics")
    stats = cursor.fetchone()
    cursor.close()
    
    return jsonify(stats)

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
