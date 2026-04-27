from functools import wraps
from flask import request, jsonify
import psycopg
from psycopg.rows import dict_row
from datetime import datetime
from core.config import Config

def require_admin_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # 1. Get token from Header or Cookie
        auth_header = request.headers.get('Authorization', '')
        token = None
        
        if auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
        
        if not token:
            token = request.cookies.get('admin_session')
        
        if not token:
            return jsonify({
                "error": "غير مصرّح - يرجى تسجيل الدخول / Unauthorized", 
                "code": "AUTH_REQUIRED"
            }), 401
        
        # 2. Check in DB
        try:
            conn = psycopg.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                dbname=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                row_factory=dict_row
            )
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT admin_id FROM admin_sessions "
                        "WHERE token = %s AND expires_at > NOW() AND is_revoked = FALSE",
                        (token,)
                    )
                    session = cur.fetchone()
                    if not session:
                        return jsonify({
                            "error": "جلسة منتهية أو غير صالحة / Session invalid", 
                            "code": "INVALID_SESSION"
                        }), 401
                    
                    # Store admin_id in request for convenience
                    request.admin_id = session['admin_id']
                    
        except Exception as e:
            return jsonify({"error": f"Internal Auth Error: {str(e)}"}), 500
        finally:
            if 'conn' in locals():
                conn.close()
                
        return f(*args, **kwargs)
    return decorated
