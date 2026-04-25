import hashlib
import csv
import os
import psycopg
from psycopg.rows import dict_row
from io import StringIO
from flask import request, g

def _get_db():
    """Get DB connection from Flask g context or create new one"""
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

class AuditService:
    @staticmethod
    def _hash_identifier(value):
        if not value:
            return None
        return hashlib.sha256(value.encode('utf-8')).hexdigest()

    @staticmethod
    def _get_request_metadata():
        try:
            ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
            user_agent = request.headers.get('User-Agent')
            return ip_address, user_agent
        except Exception:
            return None, None

    @staticmethod
    def log(action_type, status='SUCCESS', nfc_uid=None, error_message=None):
        try:
            db = _get_db()
            cursor = db.cursor()
            ip_address, user_agent = AuditService._get_request_metadata()
            identifier_hash = AuditService._hash_identifier(nfc_uid)

            cursor.execute("""
                INSERT INTO audit_log 
                (action_type, nfc_uid, ip_address, user_agent, success, status, identifier_hash, error_message)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                action_type, 
                nfc_uid, 
                ip_address, 
                user_agent, 
                status == 'SUCCESS',
                status,
                identifier_hash,
                error_message
            ))
            db.commit()
            cursor.close()
        except Exception as e:
            print(f"Failed to write audit log: {e}")

    @staticmethod
    def query(action_type=None, status=None, date_from=None, date_to=None, page=1, per_page=50):
        try:
            db = _get_db()
            cursor = db.cursor()
            
            query_base = "FROM audit_log WHERE 1=1"
            params = []
            
            if action_type:
                query_base += " AND action_type = %s"
                params.append(action_type)
            if status:
                query_base += " AND status = %s"
                params.append(status)
            if date_from:
                query_base += " AND timestamp >= %s"
                params.append(date_from)
            if date_to:
                query_base += " AND timestamp <= %s"
                params.append(date_to)

            # Count total
            cursor.execute(f"SELECT COUNT(*) {query_base}", params)
            total = cursor.fetchone()[0]

            # Fetch records
            offset = (page - 1) * per_page
            query_records = f"SELECT log_id, action_type, nfc_uid, ip_address, user_agent, success, status, identifier_hash, error_message, timestamp {query_base} ORDER BY timestamp DESC LIMIT %s OFFSET %s"
            
            cursor.execute(query_records, params + [per_page, offset])
            columns = [desc[0] for desc in cursor.description]
            records = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            cursor.close()
            
            # Format timestamps to isoformat for JSON
            for r in records:
                if r['timestamp']:
                    r['timestamp'] = r['timestamp'].isoformat()
                    
            return {"logs": records, "total": total, "page": page, "per_page": per_page}
        except Exception as e:
            print(f"Error querying audit log: {e}")
            return {"logs": [], "total": 0, "page": page, "per_page": per_page}

    @staticmethod
    def get_stats():
        try:
            db = _get_db()
            cursor = db.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM audit_log")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM audit_log WHERE timestamp >= NOW() - INTERVAL '24 HOURS'")
            last_24h = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM audit_log WHERE action_type = 'VOTE_CAST' AND timestamp >= CURRENT_DATE")
            votes_today = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM audit_log WHERE status != 'SUCCESS' AND timestamp >= CURRENT_DATE")
            failed_today = cursor.fetchone()[0]
            
            cursor.execute("SELECT action_type, COUNT(*) as count FROM audit_log GROUP BY action_type ORDER BY count DESC LIMIT 5")
            top_actions = [{"action_type": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            cursor.close()
            return {
                "total": total,
                "last_24h": last_24h,
                "votes_today": votes_today,
                "failed_today": failed_today,
                "top_actions": top_actions
            }
        except Exception as e:
            print(f"Error getting audit stats: {e}")
            return {"total": 0, "last_24h": 0, "votes_today": 0, "failed_today": 0, "top_actions": []}

    @staticmethod
    def export_csv(action_type=None, status=None, date_from=None, date_to=None):
        try:
            db = _get_db()
            cursor = db.cursor()
            
            query = "SELECT log_id, timestamp, action_type, status, identifier_hash, ip_address, error_message FROM audit_log WHERE 1=1"
            params = []
            
            if action_type:
                query += " AND action_type = %s"
                params.append(action_type)
            if status:
                query += " AND status = %s"
                params.append(status)
            if date_from:
                query += " AND timestamp >= %s"
                params.append(date_from)
            if date_to:
                query += " AND timestamp <= %s"
                params.append(date_to)
                
            query += " ORDER BY timestamp DESC"
            
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            records = cursor.fetchall()
            
            si = StringIO()
            cw = csv.writer(si)
            cw.writerow(columns)
            cw.writerows(records)
            
            cursor.close()
            return si.getvalue()
        except Exception as e:
            print(f"Error exporting audit log: {e}")
            return ""
