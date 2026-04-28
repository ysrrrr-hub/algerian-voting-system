import os
from datetime import datetime
from flask import Blueprint, request, jsonify, Response, send_file
from psycopg.rows import dict_row
import psycopg
import bcrypt

from core.config import Config
from .auth_middleware import require_admin_auth
from services.audit_service import AuditService
from services.pv_generator import PVGenerator

admin_elections_bp = Blueprint('admin_elections', __name__)

def get_db_conn():
    return psycopg.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        dbname=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        row_factory=dict_row
    )

@admin_elections_bp.route('', methods=['GET'])
@require_admin_auth
def list_elections():
    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM elections ORDER BY id DESC")
                elections = cur.fetchall()
                for el in elections:
                    for k, v in el.items():
                        if isinstance(v, datetime):
                            el[k] = v.isoformat()
        return jsonify({"elections": elections})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_elections_bp.route('/<int:election_id>', methods=['GET'])
@require_admin_auth
def get_election_details(election_id):
    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM elections WHERE id = %s", (election_id,))
                election = cur.fetchone()
                if not election:
                    return jsonify({"error": "Election not found"}), 404
                    
                for k, v in election.items():
                    if isinstance(v, datetime):
                        election[k] = v.isoformat()

                # Basic stats
                cur.execute("SELECT COUNT(*) FROM voters")
                total_voters = cur.fetchone()['count']
                
                cur.execute("SELECT COUNT(*) FROM voters WHERE has_voted = TRUE")
                total_voted = cur.fetchone()['count']
                
                turnout = round((total_voted / total_voters * 100) if total_voters > 0 else 0, 2)
                
                cur.execute("SELECT COUNT(*) FROM candidates WHERE is_active = TRUE")
                candidates_count = cur.fetchone()['count']
                
                # Fetch Blockchain Integrity dynamically
                from blockchain.chain import Blockchain
                bc = Blockchain(db_connection=conn)
                bc.load_chain_from_db()
                blockchain_valid = bc.verify_integrity()
                blockchain_blocks = len(bc.chain)

                # votes_per_candidate
                cur.execute("""
                    SELECT c.candidate_id, c.full_name_ar as name_ar, c.full_name_fr as name_fr, c.party_name_ar as party_ar,
                           COUNT(v.id) as votes_count
                    FROM candidates c
                    LEFT JOIN votes v ON v.candidate_id = c.candidate_id
                    WHERE c.is_active = TRUE
                    GROUP BY c.candidate_id, c.full_name_ar, c.full_name_fr, c.party_name_ar
                    ORDER BY votes_count DESC
                """)
                votes_per_candidate = cur.fetchall()
                # Compute percents
                for vpc in votes_per_candidate:
                    vpc['percent'] = round((vpc['votes_count'] / total_voted * 100) if total_voted > 0 else 0, 2)
                    
                # By Wilaya
                cur.execute("""
                    SELECT wilaya, COUNT(*) as count 
                    FROM voters WHERE has_voted = TRUE 
                    GROUP BY wilaya ORDER BY count DESC LIMIT 10
                """)
                votes_by_wilaya = cur.fetchall()
                
                # By Gender
                cur.execute("""
                    SELECT gender, COUNT(*) as count 
                    FROM voters WHERE has_voted = TRUE 
                    GROUP BY gender
                """)
                gender_rows = cur.fetchall()
                votes_by_gender = {"M": 0, "F": 0}
                for gr in gender_rows:
                     if gr['gender'] in votes_by_gender:
                          votes_by_gender[gr['gender']] = gr['count']
                          
                # By hour (timeline)
                cur.execute("""
                    SELECT EXTRACT(HOUR FROM voted_at) as hour, COUNT(*) as count 
                    FROM voters WHERE has_voted = TRUE AND voted_at IS NOT NULL
                    GROUP BY hour ORDER BY hour ASC
                """)
                votes_by_hour = cur.fetchall()

                stats = {
                    "total_voters": total_voters,
                    "total_voted": total_voted,
                    "turnout_percent": turnout,
                    "candidates_count": candidates_count,
                    "votes_per_candidate": votes_per_candidate,
                    "votes_by_wilaya": votes_by_wilaya,
                    "votes_by_gender": votes_by_gender,
                    "votes_by_hour": votes_by_hour,
                    "blockchain_valid": blockchain_valid,
                    "blockchain_blocks": blockchain_blocks
                }

        return jsonify({"election": election, "stats": stats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_elections_bp.route('', methods=['POST'])
@require_admin_auth
def create_election():
    data = request.get_json(silent=True) or {}
    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO elections (name_ar, name_fr, election_type, start_date, end_date, min_turnout_percent, status)
                    VALUES (%s, %s, %s, %s, %s, %s, 'DRAFT')
                    RETURNING id
                """, (
                    data['name_ar'], data['name_fr'], data['election_type'],
                    data['start_date'], data['end_date'], data.get('min_turnout_percent', 0.0)
                ))
                new_id = cur.fetchone()['id']
                conn.commit()
                AuditService.log('ELECTION_CREATED', details=f"id={new_id}")
                return jsonify({"success": True, "id": new_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_elections_bp.route('/<int:election_id>', methods=['PUT'])
@require_admin_auth
def update_election(election_id):
    data = request.get_json(silent=True) or {}
    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT status FROM elections WHERE id = %s", (election_id,))
                election = cur.fetchone()
                if not election: return jsonify({"error": "Election not found"}), 404
                if election['status'] in ('CLOSED', 'CANCELLED'):
                    return jsonify({"error": "You cannot edit closed/cancelled elections."}), 400
                    
                cur.execute("""
                    UPDATE elections SET name_ar=%s, name_fr=%s, election_type=%s, start_date=%s, end_date=%s, min_turnout_percent=%s
                    WHERE id = %s
                """, (
                    data['name_ar'], data['name_fr'], data['election_type'],
                    data['start_date'], data['end_date'], data.get('min_turnout_percent', 0.0), election_id
                ))
                conn.commit()
                AuditService.log('ELECTION_UPDATED', details=f"id={election_id}")
                return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_elections_bp.route('/<int:election_id>/publish', methods=['POST'])
@require_admin_auth
def publish_election(election_id):
    data = request.get_json(silent=True) or {}
    pwd = data.get('admin_password')
    if not pwd: return jsonify({"error": "Admin password required"}), 400
    
    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT password_hash FROM admin_users WHERE admin_id = %s", (request.admin_id,))
                admin = cur.fetchone()
                if not admin or not bcrypt.checkpw(pwd.encode('utf-8'), admin['password_hash'].encode() if isinstance(admin['password_hash'], str) else admin['password_hash']):
                    return jsonify({"error": "كلمة المرور غير صحيحة"}), 401

                cur.execute("SELECT start_date FROM elections WHERE id = %s", (election_id,))
                election = cur.fetchone()
                new_status = 'OPEN' if datetime.now().astimezone() >= election['start_date'] else 'SCHEDULED'
                
                cur.execute("UPDATE elections SET status = %s WHERE id = %s", (new_status, election_id))
                conn.commit()
                AuditService.log('ELECTION_PUBLISHED', details=f"id={election_id}, new_status={new_status}")
                return jsonify({"success": True, "status": new_status})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_elections_bp.route('/<int:election_id>/close', methods=['POST'])
@require_admin_auth
def close_election(election_id):
    data = request.get_json(silent=True) or {}
    pwd = data.get('admin_password')
    notes = data.get('notes', '')
    if not pwd: return jsonify({"error": "Admin password required"}), 400

    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT username, password_hash FROM admin_users WHERE admin_id = %s", (request.admin_id,))
                admin = cur.fetchone()
                if not admin or not bcrypt.checkpw(pwd.encode('utf-8'), admin['password_hash'].encode() if isinstance(admin['password_hash'], str) else admin['password_hash']):
                    return jsonify({"error": "كلمة المرور غير صحيحة"}), 401

                cur.execute("SELECT status FROM elections WHERE id = %s", (election_id,))
                election = cur.fetchone()
                if election['status'] not in ('OPEN', 'PRELIMINARY'):
                    return jsonify({"error": "Can only close OPEN or PRELIMINARY elections"}), 400
                    
                cur.execute("SELECT COUNT(*) FROM voters")
                total_voters = cur.fetchone()['count']
                cur.execute("SELECT COUNT(*) FROM voters WHERE has_voted = TRUE")
                total_voted = cur.fetchone()['count']
                turnout = round((total_voted / total_voters * 100) if total_voters > 0 else 0, 2)
                
                cur.execute("""
                    SELECT c.candidate_id, COUNT(v.id) as votes
                    FROM candidates c
                    LEFT JOIN votes v ON v.candidate_id = c.candidate_id
                    GROUP BY c.candidate_id ORDER BY votes DESC LIMIT 1
                """)
                winner = cur.fetchone()
                winner_id = winner['candidate_id'] if winner else None

                cur.execute("""
                    UPDATE elections 
                    SET status = 'CLOSED', official_close_date = NOW(), official_close_by = %s, turnout_percent = %s, final_winner_id = %s, notes = %s
                    WHERE id = %s
                """, (admin['username'], turnout, winner_id, notes, election_id))
                conn.commit()
                AuditService.log('ELECTION_CLOSED', details=f"id={election_id}, turnout={turnout}, winner={winner_id}")
                return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_elections_bp.route('/<int:election_id>/cancel', methods=['POST'])
@require_admin_auth
def cancel_election(election_id):
    data = request.get_json(silent=True) or {}
    pwd = data.get('admin_password')
    reason = data.get('reason', '')
    if not pwd: return jsonify({"error": "Admin password required"}), 400

    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT password_hash FROM admin_users WHERE admin_id = %s", (request.admin_id,))
                admin = cur.fetchone()
                if not admin or not bcrypt.checkpw(pwd.encode('utf-8'), admin['password_hash'].encode() if isinstance(admin['password_hash'], str) else admin['password_hash']):
                    return jsonify({"error": "كلمة المرور غير صحيحة"}), 401

                cur.execute("SELECT status FROM elections WHERE id = %s", (election_id,))
                if cur.fetchone()['status'] == 'CLOSED':
                     return jsonify({"error": "Cannot cancel CLOSED election"}), 400

                cur.execute("UPDATE elections SET status = 'CANCELLED', notes = %s WHERE id = %s", (reason, election_id))
                conn.commit()
                AuditService.log('ELECTION_CANCELLED', details=f"id={election_id}")
                return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_elections_bp.route('/<int:election_id>/preliminary', methods=['POST'])
@require_admin_auth
def preliminary_election(election_id):
    data = request.get_json(silent=True) or {}
    pwd = data.get('admin_password')
    if not pwd: return jsonify({"error": "Admin password required"}), 400

    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT password_hash FROM admin_users WHERE admin_id = %s", (request.admin_id,))
                admin = cur.fetchone()
                if not admin or not bcrypt.checkpw(pwd.encode('utf-8'), admin['password_hash'].encode() if isinstance(admin['password_hash'], str) else admin['password_hash']):
                    return jsonify({"error": "كلمة المرور غير صحيحة"}), 401
                    
                cur.execute("UPDATE elections SET status = 'PRELIMINARY' WHERE id = %s AND status = 'OPEN'", (election_id,))
                if cur.rowcount == 0:
                     return jsonify({"error": "Election is not OPEN"}), 400
                     
                conn.commit()
                AuditService.log('ELECTION_PRELIMINARY_RESULTS', details=f"id={election_id}")
                return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_elections_bp.route('/<int:election_id>/pv-pdf', methods=['GET'])
@require_admin_auth
def download_pv(election_id):
    # This might require app context to run the inner API locally or we just rewrite the fetching.
    try:
        req_res, _ = get_election_details(election_id)
        # get_election_details returns a tuple when used physically, actually it returns Response obj. Let's unpack the json payload
        payload = req_res.get_json()
        if 'error' in payload:
            return jsonify(payload), 400
            
        election = payload['election']
        stats = payload['stats']
        
        if election['status'] != 'CLOSED':
            return jsonify({"error": "يجب إقفال الانتخابات أولاً"}), 400
            
        pv_dir = "/opt/algerian-voting-system/uploads/pv"
        if not os.path.exists(pv_dir): os.makedirs(pv_dir, exist_ok=True)
            
        filename = f"election_{election_id}_{int(datetime.utcnow().timestamp())}.pdf"
        output_path = os.path.join(pv_dir, filename)
        
        PVGenerator.generate_pv(election, stats, output_path)
        
        pv_url = f"/uploads/pv/{filename}"
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE elections SET pv_url = %s, pv_generated_at = NOW() WHERE id = %s", (pv_url, election_id))
                conn.commit()
        
        AuditService.log('PV_GENERATED', details=f"id={election_id}, url={pv_url}")
        
        return send_file(output_path, as_attachment=True, download_name=f"PV_Election_{election_id}.pdf", mimetype="application/pdf")
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
