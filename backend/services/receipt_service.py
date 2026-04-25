import secrets
import os
import psycopg
from psycopg.rows import dict_row
from flask import g

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

class ReceiptService:
    @staticmethod
    def generate_receipt(vote_hash, block_hash, block_index, election_id=1):
        db = _get_db()
        cursor = db.cursor()
        
        # Generate a unique receipt code format ALG-2026-XXXXXXXX
        while True:
            random_part = secrets.token_hex(4).upper()
            receipt_code = f"ALG-2026-{random_part}"
            
            # Check for uniqueness
            cursor.execute("SELECT 1 FROM vote_receipts WHERE receipt_code = %s", (receipt_code,))
            if not cursor.fetchone():
                break

        cursor.execute("""
            INSERT INTO vote_receipts 
            (receipt_code, vote_hash, block_hash, block_index, election_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (receipt_code, vote_hash, block_hash, block_index, election_id))
        
        cursor.close()
        # Note: Do not commit here if it's meant to be within a broader transaction.
        # It's better not to call db.commit() here since the route will call it at the very end to keep Atomicity!
        # The prompt says: "بعد commit الناجح، استدع ReceiptService.generate_receipt() ضمن نفس transaction (أو بعدها مباشرة)"
        # So we won't call commit here if we don't need to, but the method needs to be resilient.
        
        return {
            "code": receipt_code,
            "verification_url": f"https://evotingdz.live/verify/{receipt_code}",
            "qr_data": f"https://evotingdz.live/verify/{receipt_code}",
            "block_hash": block_hash,
            "block_index": block_index
        }

    @staticmethod
    def verify_receipt(receipt_code):
        try:
            db = _get_db()
            cursor = db.cursor()
            
            cursor.execute("""
                SELECT 
                    r.receipt_code, 
                    r.timestamp, 
                    r.block_hash, 
                    r.block_index,
                    r.verified_count,
                    e.name_ar as election_name_ar,
                    e.name_fr as election_name_fr
                FROM vote_receipts r
                LEFT JOIN elections e ON r.election_id = e.id
                WHERE r.receipt_code = %s
            """, (receipt_code,))
            
            record = cursor.fetchone()
            
            if record:
                # Increment verification count
                cursor.execute("""
                    UPDATE vote_receipts 
                    SET verified_count = verified_count + 1, last_verified_at = NOW() 
                    WHERE receipt_code = %s
                """, (receipt_code,))
                db.commit()
                
                result = {
                    "verified": True,
                    "receipt_code": record['receipt_code'],
                    "timestamp": record['timestamp'].isoformat() if record['timestamp'] else None,
                    "block_hash": record['block_hash'],
                    "block_index": record['block_index'],
                    "verified_count": record['verified_count'] + 1,
                    "election_name_ar": record['election_name_ar'],
                    "election_name_fr": record['election_name_fr'],
                    "message_ar": "الوصل صحيح ومسجل في النظام",
                    "message_fr": "Le reçu est valide et enregistré dans le système",
                    "privacy_note_ar": "🔒 لا يكشف هذا التحقق عن المرشّح الذي صوّتَ له — السرية محفوظة",
                    "privacy_note_fr": "🔒 Confidentialité préservée — Ce reçu ne révèle pas le candidat"
                }
                cursor.close()
                return result
            else:
                cursor.close()
                return {
                    "verified": False,
                    "message_ar": "لم يتم العثور على الوصل، يرجى التأكد من الرمز",
                    "message_fr": "Reçu introuvable, veuillez vérifier le code"
                }
        except Exception as e:
            print(f"Error verifying receipt: {e}")
            return {
                "verified": False,
                "message_ar": "حدث خطأ أثناء الاتصال بقاعدة البيانات",
                "message_fr": "Erreur de connexion à la base de données"
            }
