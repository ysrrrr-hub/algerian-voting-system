import os
import uuid
from flask import Blueprint, request, jsonify
import psycopg
from psycopg.rows import dict_row
from core.config import Config
from services.audit_service import AuditService
from .auth_middleware import require_admin_auth

admin_candidates_bp = Blueprint('admin_candidates', __name__)

UPLOADS_DIR = "/opt/algerian-voting-system/uploads/candidates"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_conn():
    return psycopg.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        dbname=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        row_factory=dict_row
    )

@admin_candidates_bp.route('', methods=['GET'])
@require_admin_auth
def list_candidates():
    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT candidate_id as id, name_ar, name_fr, party_ar, party_fr, 
                           color, photo_url, bio_ar, bio_fr 
                    FROM candidates 
                    ORDER BY id ASC
                """)
                candidates = cur.fetchall()
                
                # Transform photo_url to full URL for frontend convenience if needed
                # However, usually relative path is safer in DB
                return jsonify(candidates)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_candidates_bp.route('', methods=['POST'])
@require_admin_auth
def create_candidate():
    try:
        name_ar = request.form.get('name_ar')
        name_fr = request.form.get('name_fr')
        party_ar = request.form.get('party_ar', '')
        party_fr = request.form.get('party_fr', '')
        color = request.form.get('color', '#006233')
        bio_ar = request.form.get('bio_ar', '')
        bio_fr = request.form.get('bio_fr', '')
        
        if not name_ar or not name_fr:
            return jsonify({"error": "الأسماء بالعربية والفرنسية مطلوبة / Names are required"}), 400
            
        photo_url = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '' and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                save_path = os.path.join(UPLOADS_DIR, filename)
                os.makedirs(UPLOADS_DIR, exist_ok=True)
                file.save(save_path)
                photo_url = f"/uploads/candidates/{filename}"
                
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO candidates (
                        name_ar, name_fr, party_ar, party_fr, color, photo_url, bio_ar, bio_fr,
                        full_name_ar, full_name_fr, party_name_ar, party_name_fr, program_summary_ar, program_summary_fr,
                        display_order, is_active
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                             (SELECT COALESCE(MAX(display_order), 0) + 1 FROM candidates), TRUE)
                    RETURNING candidate_id as id
                """, (
                    name_ar, name_fr, party_ar, party_fr, color, photo_url, bio_ar, bio_fr,
                    name_ar, name_fr, party_ar, party_fr, bio_ar, bio_fr
                ))
                new_id = cur.fetchone()['id']
                conn.commit()
                
                AuditService.log('CANDIDATE_CREATED', details=f"id={new_id}, name={name_ar}")
                return jsonify({"id": new_id, "success": True, "message": "تمت إضافة المرشح بنجاح"}), 201
                
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_candidates_bp.route('/<int:candidate_id>', methods=['PUT', 'POST']) # Support POST for multipart update sometimes
@require_admin_auth
def update_candidate(candidate_id):
    try:
        name_ar = request.form.get('name_ar')
        name_fr = request.form.get('name_fr')
        party_ar = request.form.get('party_ar')
        party_fr = request.form.get('party_fr')
        color = request.form.get('color')
        bio_ar = request.form.get('bio_ar')
        bio_fr = request.form.get('bio_fr')
        
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                # Get current photo to delete if replaced
                cur.execute("SELECT photo_url FROM candidates WHERE candidate_id = %s", (candidate_id,))
                current = cur.fetchone()
                if not current:
                    return jsonify({"error": "المرشح غير موجود"}), 404
                
                photo_url = current['photo_url']
                if 'photo' in request.files:
                    file = request.files['photo']
                    if file and file.filename != '' and allowed_file(file.filename):
                        # Delete old if exists
                        if photo_url:
                            old_path = os.path.join("/opt/algerian-voting-system", photo_url.lstrip('/'))
                            if os.path.exists(old_path) and "/uploads/candidates/" in old_path:
                                try: os.remove(old_path)
                                except: pass
                                
                        ext = file.filename.rsplit('.', 1)[1].lower()
                        filename = f"{uuid.uuid4().hex}.{ext}"
                        save_path = os.path.join(UPLOADS_DIR, filename)
                        file.save(save_path)
                        photo_url = f"/uploads/candidates/{filename}"

                # Update logic - partial update support
                updates = []
                params = []
                
                fields = {
                    'name_ar': name_ar, 'name_fr': name_fr, 
                    'party_ar': party_ar, 'party_fr': party_fr,
                    'color': color, 'bio_ar': bio_ar, 'bio_fr': bio_fr,
                    'photo_url': photo_url
                }
                
                # Sync with old columns
                mapping = {
                    'name_ar': 'full_name_ar', 'name_fr': 'full_name_fr',
                    'party_ar': 'party_name_ar', 'party_fr': 'party_name_fr',
                    'bio_ar': 'program_summary_ar', 'bio_fr': 'program_summary_fr'
                }

                for k, v in fields.items():
                    if v is not None:
                        updates.append(f"{k} = %s")
                        params.append(v)
                        if k in mapping:
                            updates.append(f"{mapping[k]} = %s")
                            params.append(v)
                
                if not updates:
                    return jsonify({"message": "لا توجد تعديلات"}), 200
                    
                params.append(candidate_id)
                cur.execute(f"UPDATE candidates SET {', '.join(updates)} WHERE candidate_id = %s", tuple(params))
                conn.commit()
                
                AuditService.log('CANDIDATE_UPDATED', details=f"id={candidate_id}")
                return jsonify({"success": True, "message": "تم تحديث بيانات المرشح بنجاح"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_candidates_bp.route('/<int:candidate_id>', methods=['DELETE'])
@require_admin_auth
def delete_candidate(candidate_id):
    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                # Check for votes
                cur.execute("SELECT COUNT(*) as count FROM votes WHERE candidate_id = %s", (candidate_id,))
                if cur.fetchone()['count'] > 0:
                    return jsonify({"error": "لا يمكن حذف مرشح صوّت له ناخبون / Cannot delete candidate with votes"}), 400
                
                # Get photo path
                cur.execute("SELECT photo_url FROM candidates WHERE candidate_id = %s", (candidate_id,))
                row = cur.fetchone()
                if row and row['photo_url']:
                    path = os.path.join("/opt/algerian-voting-system", row['photo_url'].lstrip('/'))
                    if os.path.exists(path) and "/uploads/candidates/" in path:
                                try: os.remove(path)
                                except: pass
                                
                cur.execute("DELETE FROM candidates WHERE candidate_id = %s", (candidate_id,))
                conn.commit()
                
                AuditService.log('CANDIDATE_DELETED', details=f"id={candidate_id}")
                return jsonify({"success": True, "message": "تم حذف المرشح بنجاح"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
