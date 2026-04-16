"""
Audit Logging Utility
"""

import psycopg
from datetime import datetime

# Action type constants
ACTION_VOTE_CAST    = "VOTE_CAST"
ACTION_VOTE_ATTEMPT = "VOTE_ATTEMPT"
ACTION_VOTER_CHECK  = "VOTER_CHECK"
ACTION_ADMIN_LOGIN  = "ADMIN_LOGIN"
ACTION_ADMIN_LOGOUT = "ADMIN_LOGOUT"
ACTION_DECRYPT      = "DECRYPT_RESULTS"
ACTION_CHAIN_VERIFY = "CHAIN_VERIFY"
ACTION_KEY_GENERATE = "KEY_GENERATE"

def log_action(
    db_connection: psycopg.Connection,
    action_type: str,
    nfc_uid: str = None,
    ip_address: str = None,
    success: bool = True,
    error_message: str = None
):
    """
    تسجيل إجراء في Audit Log
    
    Args:
        db_connection: اتصال قاعدة البيانات
        action_type: نوع الإجراء (VOTE_CAST, LOGIN, etc.)
        nfc_uid: معرف البطاقة (إن وُجد)
        ip_address: عنوان IP
        success: هل نجح الإجراء؟
        error_message: رسالة الخطأ (إن وُجدت)
    """
    cursor = db_connection.cursor()
    
    cursor.execute("""
        INSERT INTO audit_log 
        (action_type, nfc_uid, ip_address, success, error_message)
        VALUES (%s, %s, %s, %s, %s)
    """, (action_type, nfc_uid, ip_address, success, error_message))
    
    db_connection.commit()
    cursor.close()
