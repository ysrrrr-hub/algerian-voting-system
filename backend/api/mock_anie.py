from flask import Blueprint, request, jsonify
from datetime import datetime
import psycopg
from psycopg.rows import dict_row

from core.config import Config
from services.audit_service import AuditService

anie_bp = Blueprint('anie', __name__)

def get_db_conn():
    return psycopg.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        dbname=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        row_factory=dict_row
    )

@anie_bp.route('/verify-citizen', methods=['GET'])
def verify_citizen():
    nfc_uid = request.args.get('nfc_uid')
    if not nfc_uid:
        return jsonify({"error": "Missing nfc_uid parameter"}), 400

    AuditService.log('ANIE_VERIFICATION_REQUESTED', nfc_uid=nfc_uid)

    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT national_id, full_name_ar, full_name_fr, date_of_birth, wilaya 
                    FROM voters 
                    WHERE nfc_uid = %s
                """, (nfc_uid,))
                voter = cur.fetchone()

                if voter:
                    dob = voter['date_of_birth'].isoformat() if voter['date_of_birth'] else None
                    return jsonify({
                        "verified": True,
                        "source": "ANIE Algeria Mock API",
                        "citizen": {
                            "national_id": voter['national_id'],
                            "full_name_ar": voter['full_name_ar'],
                            "full_name_fr": voter['full_name_fr'],
                            "date_of_birth": dob,
                            "wilaya": voter['wilaya'],
                            "is_eligible": True,
                            "eligibility_reason": "مواطن جزائري بالغ مسجّل"
                        },
                        "verified_at": datetime.utcnow().isoformat() + "Z"
                    })
                else:
                    return jsonify({
                        "verified": False,
                        "reason": "بطاقة غير مسجّلة في النظام الوطني",
                        "source": "ANIE Algeria Mock API"
                    }), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
