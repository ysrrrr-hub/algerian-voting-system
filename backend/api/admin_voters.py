import os
import csv
import json
import uuid
import re
from io import StringIO
from datetime import datetime, date
from flask import Blueprint, request, jsonify, Response
from psycopg.rows import dict_row
import psycopg
import bcrypt

from core.config import Config
from services.audit_service import AuditService
from .auth_middleware import require_admin_auth

admin_voters_bp = Blueprint('admin_voters', __name__)

def get_db_conn():
    return psycopg.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        dbname=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        row_factory=dict_row
    )

def validate_voter_data(data):
    errors = []
    
    # nfc_uid: regex ^[0-9A-Fa-f]{8,32}$
    nfc_uid = data.get('nfc_uid')
    if not nfc_uid or not re.match(r'^[0-9A-Fa-f]{8,32}$', nfc_uid):
        errors.append("UID الخاص بـ NFC غير صالح.")
        
    # national_id: 10 digits
    national_id = data.get('national_id')
    if not national_id or not re.match(r'^\d{10}$', national_id):
        errors.append("الرقم الوطني يجب أن يتكون من 10 أرقام.")
        
    # date_of_birth
    dob = data.get('date_of_birth')
    if not dob:
        errors.append("تاريخ الميلاد مطلوب.")
    else:
        try:
            dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
            age = (date.today() - dob_date).days / 365.25
            if age < 18:
                errors.append("الناخب يجب أن يكون عمره 18 سنة على الأقل.")
        except ValueError:
            errors.append("صيغة تاريخ الميلاد غير صالحة.")
            
    # gender
    gender = data.get('gender')
    if gender not in ('M', 'F'):
        errors.append("الجنس يجب أن يكون 'M' أو 'F'.")
        
    # wilaya (simple check for now)
    if not data.get('wilaya'):
        errors.append("الولاية مطلوبة.")
        
    # email optional regex
    email = data.get('email')
    if email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
         errors.append("البريد الإلكتروني غير صالح.")
         
    if not data.get('full_name_ar') or not data.get('full_name_fr'):
        errors.append("الأسماء بالعربية والفرنسية مطلوبة.")

    return errors

@admin_voters_bp.route('', methods=['GET'])
@require_admin_auth
def list_voters():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '')
        wilaya = request.args.get('wilaya', '')
        has_voted = request.args.get('has_voted', '')
        gender = request.args.get('gender', '')
        
        offset = (page - 1) * per_page
        
        where_clauses = []
        params = []
        
        if search:
            where_clauses.append("(nfc_uid ILIKE %s OR national_id ILIKE %s OR full_name_ar ILIKE %s OR full_name_fr ILIKE %s OR email ILIKE %s)")
            search_param = f"%{search}%"
            params.extend([search_param] * 5)
            
        if wilaya:
            where_clauses.append("wilaya = %s")
            params.append(wilaya)
            
        if has_voted.lower() in ('true', 'false'):
            where_clauses.append("has_voted = %s")
            params.append(has_voted.lower() == 'true')
            
        if gender in ('M', 'F'):
            where_clauses.append("gender = %s")
            params.append(gender)
            
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        if where_clauses:
             where_sql = "WHERE " + where_sql
        else:
             where_sql = ""

        with get_db_conn() as conn:
            with conn.cursor() as cur:
                # Count total
                cur.execute(f"SELECT COUNT(*) as total FROM voters {where_sql}", params)
                total = cur.fetchone()['total']
                
                # Fetch data
                query = f"""
                    SELECT voter_id as id, nfc_uid, national_id, full_name_ar, full_name_fr, 
                           date_of_birth, gender, wilaya, commune, phone, email, has_voted, voted_at
                    FROM voters
                    {where_sql}
                    ORDER BY voter_id DESC
                    LIMIT %s OFFSET %s
                """
                cur.execute(query, params + [per_page, offset])
                voters = cur.fetchall()
                
                # Convert dates to string for JSON serialization
                for v in voters:
                    if v['date_of_birth']:
                        v['date_of_birth'] = v['date_of_birth'].isoformat()
                    if v['voted_at']:
                        v['voted_at'] = v['voted_at'].isoformat()
                        
        total_pages = (total + per_page - 1) // per_page
        
        return jsonify({
            "voters": voters,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_voters_bp.route('/<int:voter_id>', methods=['GET'])
@require_admin_auth
def get_voter(voter_id):
    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT voter_id as id, nfc_uid, national_id, full_name_ar, full_name_fr, 
                           date_of_birth, gender, wilaya, commune, phone, email, has_voted, voted_at, registration_date
                    FROM voters WHERE voter_id = %s
                """, (voter_id,))
                voter = cur.fetchone()
                if not voter:
                    return jsonify({"error": "الناخب غير موجود"}), 404
                    
                if voter['date_of_birth']: voter['date_of_birth'] = voter['date_of_birth'].isoformat()
                if voter['voted_at']:      voter['voted_at']      = voter['voted_at'].isoformat()
                if voter['registration_date']: voter['registration_date'] = voter['registration_date'].isoformat()
                
                return jsonify(voter)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_voters_bp.route('', methods=['POST'])
@require_admin_auth
def create_voter():
    data = request.get_json(silent=True) or {}
    errors = validate_voter_data(data)
    if errors:
        return jsonify({"error": " | ".join(errors)}), 400
        
    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO voters (nfc_uid, national_id, full_name_ar, full_name_fr, date_of_birth, gender, wilaya, commune, phone, email)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING voter_id as id
                """, (
                    data['nfc_uid'], data['national_id'], data['full_name_ar'], data['full_name_fr'], 
                    data['date_of_birth'], data['gender'], data['wilaya'], data.get('commune'), 
                    data.get('phone'), data.get('email')
                ))
                new_id = cur.fetchone()['id']
                conn.commit()
                AuditService.log('VOTER_CREATED', details=f"id={new_id}, nfc_uid={data['nfc_uid']}")
                return jsonify({"success": True, "id": new_id, "message": "تمت إضافة الناخب بنجاح"}), 201
    except psycopg.errors.CheckViolation:
        return jsonify({"error": "الناخب يجب أن يكون عمره 18 سنة على الأقل (مرفوض من قاعدة البيانات)."}), 400
    except psycopg.errors.UniqueViolation as e:
        return jsonify({"error": "بطاقة الناخب أو الرقم الوطني موجود مسبقاً."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_voters_bp.route('/<int:voter_id>', methods=['PUT'])
@require_admin_auth
def update_voter(voter_id):
    data = request.get_json(silent=True) or {}
    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT has_voted FROM voters WHERE voter_id = %s", (voter_id,))
                voter = cur.fetchone()
                if not voter:
                    return jsonify({"error": "الناخب غير موجود"}), 404
                    
                if voter['has_voted'] and 'nfc_uid' in data:
                    return jsonify({"error": "لا يمكن تعديل معرف NFC لناخب صوّت بالفعل"}), 400
                    
                updates = []
                params = []
                allowed_fields = ['nfc_uid', 'national_id', 'full_name_ar', 'full_name_fr', 'date_of_birth', 'gender', 'wilaya', 'commune', 'phone', 'email']
                
                for field in allowed_fields:
                    if field in data:
                        updates.append(f"{field} = %s")
                        params.append(data[field])
                        
                if not updates:
                     return jsonify({"message": "لا توجد تعديلات"}), 200
                     
                params.append(voter_id)
                cur.execute(f"UPDATE voters SET {', '.join(updates)} WHERE voter_id = %s", tuple(params))
                conn.commit()
                AuditService.log('VOTER_UPDATED', details=f"id={voter_id}")
                return jsonify({"success": True, "message": "تم تحديث الناخب بنجاح"})
    except psycopg.errors.CheckViolation:
        return jsonify({"error": "تاريخ الميلاد المدخل غير صالح (أقل من 18 سنة)."}), 400
    except psycopg.errors.UniqueViolation:
        return jsonify({"error": "البيانات المدخلة لمُعرّف سبق تسجيله."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_voters_bp.route('/<int:voter_id>/delete', methods=['POST'])
@require_admin_auth
def delete_voter(voter_id):
    try:
        data = request.get_json(silent=True) or {}
        admin_password = data.get('admin_password')
        
        if not admin_password:
            return jsonify({"error": "يرجى إدخال كلمة مرور المشرف للتأكيد"}), 400
            
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                # Password check
                cur.execute("SELECT password_hash FROM admin_users WHERE admin_id = %s", (request.admin_id,))
                admin = cur.fetchone()
                
                if not admin:
                    AuditService.log('VOTER_DELETE_AUTH_FAILED', status='FAILED', details=f"Admin {request.admin_id} not found")
                    return jsonify({"error": "المشرف غير موجود"}), 404
                    
                pw_hash = admin['password_hash'].encode() if isinstance(admin['password_hash'], str) else admin['password_hash']
                if not bcrypt.checkpw(admin_password.encode('utf-8'), pw_hash):
                    AuditService.log('VOTER_DELETE_AUTH_FAILED', status='FAILED', details=f"Wrong password for Admin {request.admin_id}")
                    return jsonify({"error": "كلمة المرور غير صحيحة"}), 401
                    
                # Check has_voted
                cur.execute("SELECT has_voted FROM voters WHERE voter_id = %s", (voter_id,))
                voter = cur.fetchone()
                if not voter:
                    return jsonify({"error": "الناخب غير موجود"}), 404
                    
                if voter['has_voted']:
                    return jsonify({"error": "لا يمكن حذف ناخب صوّت بالفعل"}), 400
                    
                # Delete
                cur.execute("DELETE FROM voters WHERE voter_id = %s", (voter_id,))
                conn.commit()
                AuditService.log('VOTER_DELETED', details=f"id={voter_id}")
                return jsonify({"success": True, "message": "تم حذف الناخب بنجاح"})
                
    except Exception as e:
         return jsonify({"error": str(e)}), 500

@admin_voters_bp.route('/stats', methods=['GET'])
@require_admin_auth
def get_voters_stats():
    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                # Overall
                cur.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN has_voted THEN 1 ELSE 0 END) as voted,
                        SUM(CASE WHEN NOT has_voted THEN 1 ELSE 0 END) as not_voted
                    FROM voters
                """)
                overall = cur.fetchone()
                
                # By Gender
                cur.execute("""
                    SELECT gender, COUNT(*) as count 
                    FROM voters WHERE gender IS NOT NULL GROUP BY gender
                """)
                by_gender = {r['gender']: r['count'] for r in cur.fetchall()}
                
                # By Wilaya
                cur.execute("SELECT wilaya, COUNT(*) as count FROM voters GROUP BY wilaya ORDER BY count DESC")
                by_wilaya = {r['wilaya']: r['count'] for r in cur.fetchall()}
                
                # By Age Group
                cur.execute("""
                    SELECT 
                        SUM(CASE WHEN age >= 18 AND age < 30 THEN 1 ELSE 0 END) as "18-29",
                        SUM(CASE WHEN age >= 30 AND age < 45 THEN 1 ELSE 0 END) as "30-44",
                        SUM(CASE WHEN age >= 45 AND age < 60 THEN 1 ELSE 0 END) as "45-59",
                        SUM(CASE WHEN age >= 60 THEN 1 ELSE 0 END) as "60+"
                    FROM (
                        SELECT EXTRACT(YEAR FROM age(current_date, date_of_birth)) as age FROM voters WHERE date_of_birth IS NOT NULL
                    ) as age_calc
                """)
                age_stats = cur.fetchone()
                by_age_group = {k: int(v or 0) for k, v in age_stats.items()} if age_stats else {}

                return jsonify({
                    "total": int(overall['total'] or 0),
                    "voted": int(overall['voted'] or 0),
                    "not_voted": int(overall['not_voted'] or 0),
                    "by_wilaya": by_wilaya,
                    "by_gender": by_gender,
                    "by_age_group": by_age_group
                })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_voters_bp.route('/wilayas', methods=['GET'])
@require_admin_auth
def get_wilayas():
    try:
        wilayas_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'wilayas.json')
        with open(wilayas_path, 'r', encoding='utf-8') as f:
            wilayas = json.load(f)
        return jsonify(wilayas)
    except Exception as e:
         return jsonify({"error": "تعذر تحميل قائمة الولايات"}), 500

@admin_voters_bp.route('/import-csv', methods=['POST'])
@require_admin_auth
def import_csv():
    try:
        dry_run = request.args.get('dry_run', 'false').lower() == 'true'
        
        if 'file' not in request.files:
            return jsonify({"error": "ملف CSV مطلوب"}), 400
            
        file = request.files['file']
        if not file.filename.endswith('.csv'):
             return jsonify({"error": "الملف يجب أن يكون CSV"}), 400
             
        # Read file with UTF-8 BOM decoding
        stream = StringIO(file.stream.read().decode('utf-8-sig'), newline=None)
        csv_reader = csv.DictReader(stream)
        
        rows = list(csv_reader)
        if len(rows) > 10000:
            return jsonify({"error": "عدد الصفوف يتجاوز الحد الأقصى 10000"}), 400
            
        success_count = 0
        failed_count = 0
        errors = []
        
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                # Start transaction for non-dry-runs (handled implicitly by 'with conn')
                # If dry_run is true, we will just rollback at the end
                
                for idx, row in enumerate(rows, start=2): # Start at row 2 because of header
                    # Clean the row keys and values (strip whitespace)
                    clean_row = {k.strip(): v.strip() if hasattr(v, 'strip') else v for k, v in row.items() if k}
                    
                    val_errors = validate_voter_data(clean_row)
                    if val_errors:
                        failed_count += 1
                        errors.append({"row": idx, "reason": " | ".join(val_errors)})
                        continue
                        
                    try:
                        cur.execute("""
                            INSERT INTO voters (nfc_uid, national_id, full_name_ar, full_name_fr, date_of_birth, gender, wilaya, commune, phone, email)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            clean_row.get('nfc_uid'), clean_row.get('national_id'), clean_row.get('full_name_ar'), clean_row.get('full_name_fr'), 
                            clean_row.get('date_of_birth'), clean_row.get('gender'), clean_row.get('wilaya'), clean_row.get('commune'), 
                            clean_row.get('phone'), clean_row.get('email')
                        ))
                        success_count += 1
                    except psycopg.errors.UniqueViolation as e:
                         failed_count += 1
                         errors.append({"row": idx, "reason": "عنصر مكرر (NFC UID أو الرقم الوطني موجود مسبقاً)"})
                         conn.rollback()
                         break # Stop processing further on DB error
                    except psycopg.errors.CheckViolation:
                         failed_count += 1
                         errors.append({"row": idx, "reason": "خطأ في قيد قاعدة البيانات (عمر الناخب < 18)"})
                         conn.rollback()
                         break
                    except Exception as e:
                         failed_count += 1
                         errors.append({"row": idx, "reason": f"خطأ قاعدة بيانات: {str(e)}"})
                         conn.rollback()
                         break
                         
                if dry_run or failed_count > 0: # If any error, rollback the entire import
                     conn.rollback()
                     message = "محاكاة ناجحة" if dry_run else "فشل الاستيراد بسبب أخطاء"
                else:
                     conn.commit()
                     message = "تم الاستيراد بنجاح"
                     AuditService.log('VOTERS_BULK_IMPORTED', details=f"count={success_count}")

        return jsonify({
             "success_count": success_count if not (failed_count > 0 and not dry_run) else 0,
             "failed_count": failed_count,
             "errors": errors,
             "total": len(rows),
             "message": message,
             "dry_run": dry_run
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_voters_bp.route('/export-csv', methods=['GET'])
@require_admin_auth
def export_csv():
    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                     SELECT nfc_uid, national_id, full_name_ar, full_name_fr, date_of_birth, gender, wilaya, commune, phone, email, has_voted, voted_at
                     FROM voters ORDER BY voter_id ASC
                """)
                voters = cur.fetchall()
                
        output = StringIO()
        # Ensure utf-8 with BOM for Excel Arabic support
        output.write('\ufeff')
        writer = csv.DictWriter(output, fieldnames=['nfc_uid', 'national_id', 'full_name_ar', 'full_name_fr', 'date_of_birth', 'gender', 'wilaya', 'commune', 'phone', 'email', 'has_voted', 'voted_at'])
        writer.writeheader()
        
        for v in voters:
            if v['date_of_birth']: v['date_of_birth'] = v['date_of_birth'].isoformat()
            if v['voted_at']: v['voted_at'] = v['voted_at'].isoformat()
            writer.writerow(v)
            
        AuditService.log('VOTERS_EXPORTED', details=f"count={len(voters)}")
            
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=voters_2026.csv"}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
