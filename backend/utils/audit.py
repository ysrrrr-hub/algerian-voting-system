"""
Audit Logging Utility
"""

import psycopg2
from datetime import datetime


def log_action(
    db_connection: psycopg2.extensions.connection,
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
