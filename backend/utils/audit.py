"""
backend/utils/audit.py
Audit Logging — تسجيل الأحداث الأمنية

يُسجل كل إجراء في النظام في جدول audit_log
لضمان الشفافية والمراجعة اللاحقة.
"""

import psycopg
from typing import Optional

# أنواع الإجراءات المدعومة
ACTION_VOTE_CAST      = "VOTE_CAST"
ACTION_VOTE_ATTEMPT   = "VOTE_ATTEMPT"
ACTION_VOTER_CHECK    = "VOTER_CHECK"
ACTION_ADMIN_LOGIN    = "ADMIN_LOGIN"
ACTION_ADMIN_LOGOUT   = "ADMIN_LOGOUT"
ACTION_DECRYPT        = "DECRYPT_RESULTS"
ACTION_CHAIN_VERIFY   = "CHAIN_VERIFY"
ACTION_KEY_GENERATE   = "KEY_GENERATE"


def log_action(
    db_connection: psycopg.Connection,
    action_type:   str,
    nfc_uid:       Optional[str] = None,
    ip_address:    Optional[str] = None,
    user_agent:    Optional[str] = None,
    success:       bool = True,
    error_message: Optional[str] = None,
) -> None:
    """
    تسجيل إجراء في جدول audit_log.

    لا يرفع استثناءً عند الفشل — التسجيل لا يجب أن يعطّل
    العملية الأصلية.

    Args:
        db_connection : اتصال PostgreSQL نشط
        action_type   : نوع الإجراء (استخدم ثوابت ACTION_*)
        nfc_uid       : معرف بطاقة الناخب (إن وُجد)
        ip_address    : عنوان IP المصدر
        user_agent    : معلومات المتصفح/التطبيق
        success       : هل نجح الإجراء؟
        error_message : رسالة الخطأ (عند الفشل)
    """
    try:
        cursor = db_connection.cursor()
        cursor.execute(
            """
            INSERT INTO audit_log
                (action_type, nfc_uid, ip_address, user_agent,
                 success, error_message)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (action_type, nfc_uid, ip_address, user_agent,
             success, error_message),
        )
        db_connection.commit()
        cursor.close()
    except Exception as exc:
        # سجّل في console ولا تكسر تدفق التطبيق
        print(f"⚠️  Audit log failed [{action_type}]: {exc}")
