"""
backend/api/routes.py
Flask REST API — 9 نقاط نهاية

  GET  /api/health              — فحص صحة النظام
  POST /api/admin/login         — تسجيل دخول المشرفين
  POST /api/admin/logout        — تسجيل خروج المشرفين
  GET  /api/voter-status/<uid>  — التحقق من أهلية ناخب
  GET  /api/candidates          — قائمة المرشحين
  POST /api/vote                — إرسال صوت جديد
  GET  /api/verify-chain        — التحقق من سلامة البلوكشين
  GET  /api/blockchain/status   — حالة السلسلة
  GET  /api/stats               — إحصائيات حية
  POST /api/decrypt-votes       — فك تشفير النتائج (مشرفون فقط)
"""

import secrets
from datetime import datetime, timedelta

import bcrypt
from flask import Flask, g, jsonify, request
from flask_cors import CORS

from api.socket_events import emit_new_vote
from blockchain.chain import Blockchain
from core.config import Config
from core.exceptions import (
    AlreadyVotedError,
    InvalidCandidateError,
    VoterNotFoundError,
    VotingClosedError,
    VotingSystemError,
)
from database.connection import db_manager
from utils.audit import (
    ACTION_ADMIN_LOGIN,
    ACTION_ADMIN_LOGOUT,
    ACTION_CHAIN_VERIFY,
    ACTION_DECRYPT,
    ACTION_VOTE_ATTEMPT,
    ACTION_VOTE_CAST,
    ACTION_VOTER_CHECK,
    log_action,
)
from utils.qr_generator import generate_vote_qr

from .middleware import require_admin

# ============================================================ Flask init
app = Flask(__name__)
app.config["SECRET_KEY"] = Config.SECRET_KEY
CORS(app, origins="*", supports_credentials=True)


# ============================================================ Helpers
def get_db():
    if "db" not in g:
        g.db = db_manager.get_connection()
    return g.db


def get_blockchain():
    if "blockchain" not in g:
        g.blockchain = Blockchain(get_db())
    return g.blockchain


def _get(row, key, idx):
    """دعم dict (RealDictCursor) وtuple في نفس الوقت."""
    return row[key] if isinstance(row, dict) else row[idx]


@app.teardown_appcontext
def cleanup(_error):
    db = g.pop("db", None)
    if db:
        db_manager.return_connection(db)


# ============================================================ Error handlers
@app.errorhandler(VotingSystemError)
def handle_voting_error(error):
    return jsonify({
        "error_ar":    error.message_ar,
        "error_fr":    error.message_fr,
        "status_code": error.status_code,
    }), error.status_code


@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error", "detail": str(e)}), 500


# ============================================================ 1. Health
@app.route("/api/health", methods=["GET"])
def health_check():
    """فحص صحة النظام — يُستخدم من load-balancer وتطبيق Flutter."""
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT 1")
        cur.close()

        bc = get_blockchain()
        return jsonify({
            "status":           "healthy",
            "database":         "connected",
            "voting_open":      Config.VOTING_OPEN,
            "blockchain_blocks": len(bc),
            "total_votes":      bc.total_votes,
            "election_year":    Config.ELECTION_YEAR,
            "timestamp":        datetime.utcnow().isoformat() + "Z",
        })
    except Exception as exc:
        return jsonify({"status": "unhealthy", "error": str(exc)}), 503


# ============================================================ 2. Admin login
@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    """
    تسجيل دخول المشرفين.
    Body : {"username": str, "password": str}
    Return: {"token": str, "expires_in": int, "admin": {...}}
    """
    data     = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({
            "error_ar": "اسم المستخدم وكلمة المرور مطلوبان",
            "error_fr": "Nom d'utilisateur et mot de passe requis",
        }), 400

    db  = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT admin_id, password_hash, full_name, role "
        "FROM admin_users WHERE username = %s AND is_active = TRUE",
        (username,),
    )
    admin = cur.fetchone()

    if not admin:
        log_action(db, ACTION_ADMIN_LOGIN, ip_address=request.remote_addr,
                   success=False, error_message="User not found")
        cur.close()
        return jsonify({
            "error_ar": "بيانات خاطئة",
            "error_fr": "Identifiants incorrects",
        }), 401

    admin_id      = _get(admin, "admin_id",      0)
    password_hash = _get(admin, "password_hash", 1)
    full_name     = _get(admin, "full_name",      2)
    role          = _get(admin, "role",           3)

    if not bcrypt.checkpw(password.encode(), password_hash.encode()):
        log_action(db, ACTION_ADMIN_LOGIN, ip_address=request.remote_addr,
                   success=False, error_message="Wrong password")
        cur.close()
        return jsonify({
            "error_ar": "كلمة مرور خاطئة",
            "error_fr": "Mot de passe incorrect",
        }), 401

    token      = secrets.token_hex(64)
    expires_at = datetime.now() + timedelta(hours=Config.SESSION_EXPIRY_HOURS)

    cur.execute(
        "INSERT INTO admin_sessions (admin_id, token, expires_at) VALUES (%s, %s, %s)",
        (admin_id, token, expires_at),
    )
    cur.execute(
        "UPDATE admin_users SET last_login = NOW() WHERE admin_id = %s",
        (admin_id,),
    )
    db.commit()
    cur.close()

    log_action(db, ACTION_ADMIN_LOGIN, ip_address=request.remote_addr, success=True)

    return jsonify({
        "success":    True,
        "token":      token,
        "expires_in": Config.SESSION_EXPIRY_HOURS * 3600,
        "admin":      {"full_name": full_name, "role": role},
    })


# ============================================================ 3. Admin logout
@app.route("/api/admin/logout", methods=["POST"])
@require_admin
def admin_logout():
    """إلغاء Token الجلسة الحالية."""
    auth   = request.headers.get("Authorization", "")[7:]
    db     = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE admin_sessions SET is_revoked = TRUE WHERE token = %s",
        (auth,),
    )
    db.commit()
    cursor.close()
    log_action(db, ACTION_ADMIN_LOGOUT, ip_address=request.remote_addr, success=True)
    return jsonify({"success": True, "message_ar": "تم تسجيل الخروج"})


# ============================================================ 4. Voter status
@app.route("/api/voter-status/<nfc_uid>", methods=["GET"])
def check_voter_status(nfc_uid: str):
    """
    التحقق من أهلية الناخب عبر NFC UID.
    Return: {eligible, message, name_ar, name_fr, has_voted}
    """
    db  = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM check_voter_eligibility(%s)", (nfc_uid,))
    result = cur.fetchone()
    cur.close()

    if not result:
        log_action(db, ACTION_VOTER_CHECK, nfc_uid=nfc_uid,
                   ip_address=request.remote_addr, success=False,
                   error_message="Not found")
        raise VoterNotFoundError()

    eligible  = _get(result, "eligible",       0)
    message   = _get(result, "message",        1)
    name_ar   = _get(result, "voter_name_ar",  2)
    name_fr   = _get(result, "voter_name_fr",  3)

    log_action(db, ACTION_VOTER_CHECK, nfc_uid=nfc_uid,
               ip_address=request.remote_addr, success=True)

    return jsonify({
        "eligible":  eligible,
        "message":   message,
        "name_ar":   name_ar,
        "name_fr":   name_fr,
        "has_voted": not eligible,
    })


# ============================================================ 5. Candidates
@app.route("/api/candidates", methods=["GET"])
def get_candidates():
    """قائمة المرشحين النشطين مرتبة حسب display_order."""
    db  = get_db()
    cur = db.cursor()
    cur.execute(
        """
        SELECT candidate_id, full_name_ar, full_name_fr,
               party_name_ar, party_name_fr, photo_url,
               program_summary_ar, program_summary_fr,
               display_order
        FROM candidates
        WHERE is_active = TRUE
        ORDER BY display_order ASC
        """
    )
    rows = cur.fetchall()
    cur.close()
    # تحويل RealDictRow لـ list من dicts
    return jsonify([dict(r) for r in rows])


# ============================================================ 6. Cast vote
@app.route("/api/vote", methods=["POST"])
def cast_vote():
    """
    استقبال صوت جديد.
    Body : {"nfc_uid": str, "candidate_id": int}
    Return: {success, vote_hash, qr_code, timestamp}
    """
    if not Config.VOTING_OPEN:
        raise VotingClosedError()

    data         = request.get_json(silent=True) or {}
    nfc_uid      = data.get("nfc_uid", "").strip()
    candidate_id = data.get("candidate_id")

    if not nfc_uid or not candidate_id:
        return jsonify({
            "error_ar": "nfc_uid و candidate_id مطلوبان",
            "error_fr": "nfc_uid et candidate_id sont requis",
        }), 400

    db  = get_db()
    cur = db.cursor()

    # 1. التحقق من أهلية الناخب
    cur.execute("SELECT * FROM check_voter_eligibility(%s)", (nfc_uid,))
    voter = cur.fetchone()

    if not voter:
        log_action(db, ACTION_VOTE_ATTEMPT, nfc_uid=nfc_uid,
                   ip_address=request.remote_addr, success=False,
                   error_message="Not found")
        cur.close()
        raise VoterNotFoundError()

    eligible = _get(voter, "eligible", 0)
    message  = _get(voter, "message",  1)

    if not eligible:
        log_action(db, ACTION_VOTE_ATTEMPT, nfc_uid=nfc_uid,
                   ip_address=request.remote_addr, success=False,
                   error_message=message)
        cur.close()
        raise AlreadyVotedError()

    # 2. التحقق من صحة المرشح
    cur.execute(
        "SELECT candidate_id FROM candidates "
        "WHERE candidate_id = %s AND is_active = TRUE",
        (candidate_id,),
    )
    if not cur.fetchone():
        log_action(db, ACTION_VOTE_ATTEMPT, nfc_uid=nfc_uid,
                   ip_address=request.remote_addr, success=False,
                   error_message="Invalid candidate")
        cur.close()
        raise InvalidCandidateError()

    try:
        # 3. تسجيل الصوت في البلوكشين
        bc         = get_blockchain()
        vote_hash  = bc.add_vote(
            {"candidate_id": candidate_id, "nfc_uid": nfc_uid},
            Config.PUBLIC_KEY_PATH,
        )

        # 4. تحديث حالة الناخب (تصويت واحد فقط)
        cur.execute(
            "UPDATE voters SET has_voted = TRUE, voted_at = NOW() "
            "WHERE nfc_uid = %s",
            (nfc_uid,),
        )
        db.commit()

        # 5. توليد QR Code للإيصال
        qr_code = generate_vote_qr(vote_hash)

        # 6. إشعار Dashboard عبر Socket.IO (real-time)
        emit_new_vote(
            blockchain_length=len(bc),
            timestamp=datetime.utcnow(),
        )

        log_action(db, ACTION_VOTE_CAST, nfc_uid=nfc_uid,
                   ip_address=request.remote_addr, success=True)
        cur.close()

        return jsonify({
            "success":    True,
            "vote_hash":  vote_hash,
            "qr_code":    qr_code,
            "message_ar": "تم تسجيل صوتك بنجاح",
            "message_fr": "Vote enregistré avec succès",
            "timestamp":  datetime.utcnow().isoformat() + "Z",
        })

    except VotingSystemError:
        raise
    except Exception as exc:
        db.rollback()
        cur.close()
        log_action(db, ACTION_VOTE_ATTEMPT, nfc_uid=nfc_uid,
                   ip_address=request.remote_addr, success=False,
                   error_message=str(exc))
        return jsonify({
            "error_ar": "فشل تسجيل الصوت",
            "error_fr": "Échec de l'enregistrement du vote",
            "details":  str(exc),
        }), 500


# ============================================================ 7. Verify chain
@app.route("/api/verify-chain", methods=["GET"])
def verify_chain():
    """التحقق من سلامة سلسلة البلوكشين بالكامل."""
    bc       = get_blockchain()
    is_valid, message = bc.verify_integrity()

    log_action(get_db(), ACTION_CHAIN_VERIFY,
               ip_address=request.remote_addr, success=is_valid)

    return jsonify({
        "valid":           is_valid,
        "message":         message,
        "chain_length":    len(bc),
        "last_block_hash": bc.last_block.hash if bc.last_block else None,
    })


# ============================================================ 8. Blockchain status
@app.route("/api/blockchain/status", methods=["GET"])
def blockchain_status():
    """معلومات تفصيلية عن حالة سلسلة الكتل."""
    bc = get_blockchain()
    return jsonify({
        "total_blocks": len(bc),
        "total_votes":  bc.total_votes,
        "last_block":   bc.last_block.to_dict() if bc.last_block else None,
    })


# ============================================================ 9. Statistics
@app.route("/api/stats", methods=["GET"])
def get_statistics():
    """إحصائيات التصويت الحية من view voting_statistics."""
    db  = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM voting_statistics")
    stats = cur.fetchone()
    cur.close()
    return jsonify(dict(stats) if stats else {})


# ============================================================ 10. Decrypt
@app.route("/api/decrypt-votes", methods=["POST"])
@require_admin
def decrypt_votes():
    """
    فك تشفير جميع الأصوات وإعادة النتائج (مشرفون فقط).
    Body : {"private_key_password": str}
    """
    data     = request.get_json(silent=True) or {}
    password = data.get("private_key_password", "")

    if not password:
        return jsonify({
            "error_ar": "كلمة مرور المفتاح الخاص مطلوبة",
            "error_fr": "Mot de passe de la clé privée requis",
        }), 400

    try:
        bc    = get_blockchain()
        votes = bc.decrypt_all_votes(Config.PRIVATE_KEY_PATH, password)

        # تجميع الأصوات حسب المرشح
        tally = {}
        for v in votes:
            cid = v["candidate_id"]
            tally[cid] = tally.get(cid, 0) + 1

        # جلب أسماء المرشحين
        db  = get_db()
        cur = db.cursor()
        cur.execute(
            "SELECT candidate_id, full_name_ar, full_name_fr FROM candidates"
        )
        cands = {_get(r, "candidate_id", 0): r for r in cur.fetchall()}
        cur.close()

        total = len(votes)
        results = []
        for cid, count in sorted(tally.items(), key=lambda x: x[1], reverse=True):
            c = cands.get(cid, {})
            results.append({
                "candidate_id": cid,
                "name_ar":      _get(c, "full_name_ar", 0) if c else "غير معروف",
                "name_fr":      _get(c, "full_name_fr", 1) if c else "Inconnu",
                "votes":        count,
                "percentage":   round(count / total * 100, 2) if total else 0,
            })

        log_action(db, ACTION_DECRYPT,
                   ip_address=request.remote_addr, success=True)

        return jsonify({
            "success":     True,
            "total_votes": total,
            "results":     results,
        })

    except ValueError as exc:
        log_action(get_db(), ACTION_DECRYPT,
                   ip_address=request.remote_addr, success=False,
                   error_message=str(exc))
        return jsonify({
            "error_ar": "فشل فك التشفير — كلمة مرور خاطئة",
            "error_fr": "Échec du déchiffrement — mot de passe incorrect",
            "details":  str(exc),
        }), 400


# ============================================================ 11. Audit Log
@app.route("/api/audit-log", methods=["GET"])
@require_admin
def get_audit_log():
    """
    جلب سجل المراجعة الأمنية (مشرفون فقط).
    Query params: action_type, limit (default 200), offset (default 0)
    """
    action_type = request.args.get("action_type")
    limit       = min(int(request.args.get("limit",  200)), 500)
    offset      = int(request.args.get("offset", 0))

    db  = get_db()
    cur = db.cursor()

    if action_type:
        cur.execute(
            """
            SELECT log_id, action_type, nfc_uid, ip_address,
                   success, error_message, timestamp
            FROM audit_log
            WHERE action_type = %s
            ORDER BY timestamp DESC
            LIMIT %s OFFSET %s
            """,
            (action_type, limit, offset),
        )
    else:
        cur.execute(
            """
            SELECT log_id, action_type, nfc_uid, ip_address,
                   success, error_message, timestamp
            FROM audit_log
            ORDER BY timestamp DESC
            LIMIT %s OFFSET %s
            """,
            (limit, offset),
        )

    rows = cur.fetchall()

    # عدد إجمالي
    cur.execute("SELECT COUNT(*) FROM audit_log" +
                (" WHERE action_type = %s" if action_type else ""),
                *([( action_type,)] if action_type else []))
    total = cur.fetchone()
    total = list(total.values())[0] if isinstance(total, dict) else total[0]
    cur.close()

    return jsonify({
        "logs":  [dict(r) for r in rows],
        "total": total,
        "limit": limit,
        "offset": offset,
    })


# ============================================================ 12. Blockchain All Blocks
@app.route("/api/blockchain/all", methods=["GET"])
@require_admin
def get_all_blocks():
    """
    جلب جميع كتل البلوكشين (مشرفون فقط).
    Query params: limit (default 100), offset (default 0)
    """
    limit  = min(int(request.args.get("limit",  100)), 1000)
    offset = int(request.args.get("offset", 0))

    db  = get_db()
    cur = db.cursor()
    cur.execute(
        """
        SELECT block_index, timestamp, encrypted_vote,
               previous_hash, current_hash, nonce
        FROM blockchain
        ORDER BY block_index DESC
        LIMIT %s OFFSET %s
        """,
        (limit, offset),
    )
    rows = cur.fetchall()

    cur.execute("SELECT COUNT(*) FROM blockchain")
    total_row = cur.fetchone()
    total = list(total_row.values())[0] if isinstance(total_row, dict) else total_row[0]
    cur.close()

    return jsonify({
        "blocks": [dict(r) for r in rows],
        "total":  total,
        "limit":  limit,
        "offset": offset,
    })


# ============================================================ 13. Stats by Wilaya
@app.route("/api/stats/wilaya", methods=["GET"])
@require_admin
def get_stats_by_wilaya():
    """إحصائيات التصويت مفصّلة حسب الولاية (مشرفون فقط)."""
    db  = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM get_stats_by_wilaya()")
    rows = cur.fetchall()
    cur.close()
    return jsonify([dict(r) for r in rows])
