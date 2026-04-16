"""
backend/api/middleware.py
Authentication Middleware — التحقق من صلاحية جلسات المشرفين

يوفر decorator @require_admin لحماية endpoints المحمية.
"""

from datetime import datetime
from functools import wraps

from flask import g, jsonify, request


def require_admin(f):
    """
    Decorator لحماية نقاط النهاية المخصصة للمشرفين.

    الاستخدام:
        @app.route('/api/admin/action')
        @require_admin
        def protected():
            admin = g.admin   # معلومات المشرف المسجّل
            ...

    يتحقق من:
      1. وجود header: Authorization: Bearer <token>
      2. Token موجود في admin_sessions ولم يُلغَ
      3. Token لم تنتهِ صلاحيته
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({
                "error_ar": "غير مصرح — Token مطلوب",
                "error_fr": "Non autorisé — Token requis",
            }), 401

        token = auth_header[7:].strip()
        if not token:
            return jsonify({
                "error_ar": "Token فارغ",
                "error_fr": "Token vide",
            }), 401

        try:
            from database.connection import db_manager

            conn   = db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT s.admin_id, s.expires_at, s.is_revoked,
                       a.username, a.role, a.full_name
                FROM admin_sessions s
                JOIN admin_users    a ON s.admin_id = a.admin_id
                WHERE s.token = %s
                  AND a.is_active = TRUE
                LIMIT 1
                """,
                (token,),
            )
            session = cursor.fetchone()
            cursor.close()
            db_manager.return_connection(conn)

            if not session:
                return jsonify({
                    "error_ar": "Token غير صالح",
                    "error_fr": "Token invalide",
                }), 401

            # دعم dict و tuple
            def _get(row, key, idx):
                return row[key] if isinstance(row, dict) else row[idx]

            is_revoked = _get(session, "is_revoked", 2)
            expires_at = _get(session, "expires_at", 1)

            if is_revoked:
                return jsonify({
                    "error_ar": "تم إلغاء الجلسة",
                    "error_fr": "Session révoquée",
                }), 401

            if datetime.now() > expires_at:
                return jsonify({
                    "error_ar": "انتهت صلاحية الجلسة",
                    "error_fr": "Session expirée",
                }), 401

            g.admin = {
                "admin_id":  _get(session, "admin_id",  0),
                "username":  _get(session, "username",  3),
                "role":      _get(session, "role",      4),
                "full_name": _get(session, "full_name", 5),
            }

            return f(*args, **kwargs)

        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    return decorated
