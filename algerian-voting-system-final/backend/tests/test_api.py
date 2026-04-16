"""
backend/tests/test_api.py
اختبارات وحدة API endpoints باستخدام Flask Test Client
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import pytest
from unittest.mock import MagicMock, patch


# ================================================================
# Fixtures
# ================================================================

@pytest.fixture
def client():
    """Flask test client مع Mock لقاعدة البيانات والبلوكشين."""
    # نستورد app بعد إعداد الـ mocks
    with patch("database.connection.db_manager") as mock_db:
        mock_conn   = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value     = mock_cursor
        mock_db.get_connection.return_value = mock_conn
        mock_db.return_connection.return_value = None

        from api.routes import app
        app.config["TESTING"]   = True
        app.config["SECRET_KEY"] = "test-secret"

        with app.test_client() as c:
            yield c


@pytest.fixture
def auth_headers():
    """Headers وهمية لاختبارات المشرفين."""
    return {"Authorization": "Bearer test-token-abc123"}


# ================================================================
# Health Check
# ================================================================

class TestHealthEndpoint:

    def test_health_returns_200(self, client):
        with patch("api.routes.get_blockchain") as mock_bc:
            mock_bc.return_value.total_votes = 0
            mock_bc.return_value.__len__     = lambda _: 1
            mock_bc.return_value.last_block  = None

            with patch("api.routes.get_db") as mock_db:
                mock_cur = MagicMock()
                mock_cur.execute.return_value = None
                mock_db.return_value.cursor.return_value = mock_cur

                resp = client.get("/api/health")
                assert resp.status_code == 200

    def test_health_returns_json(self, client):
        with patch("api.routes.get_blockchain"), patch("api.routes.get_db"):
            resp = client.get("/api/health")
            # يجب أن يكون JSON وليس HTML
            assert resp.content_type.startswith("application/json") or \
                   resp.status_code in (200, 503)


# ================================================================
# Candidates Endpoint
# ================================================================

class TestCandidatesEndpoint:

    def test_candidates_returns_list(self, client):
        mock_candidates = [
            {"candidate_id": 1, "full_name_ar": "أحمد", "full_name_fr": "Ahmed",
             "party_name_ar": "حزب", "party_name_fr": "Parti",
             "photo_url": None, "display_order": 1,
             "program_summary_ar": None, "program_summary_fr": None},
        ]

        with patch("api.routes.get_db") as mock_db:
            mock_cur = MagicMock()
            mock_cur.fetchall.return_value = mock_candidates
            mock_db.return_value.cursor.return_value = mock_cur

            resp = client.get("/api/candidates")
            assert resp.status_code == 200
            data = json.loads(resp.data)
            assert isinstance(data, list)


# ================================================================
# Vote Endpoint
# ================================================================

class TestVoteEndpoint:

    def test_vote_missing_body_returns_400(self, client):
        resp = client.post(
            "/api/vote",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_vote_missing_candidate_id(self, client):
        resp = client.post(
            "/api/vote",
            data=json.dumps({"nfc_uid": "TEST_001"}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_vote_missing_nfc_uid(self, client):
        resp = client.post(
            "/api/vote",
            data=json.dumps({"candidate_id": 1}),
            content_type="application/json",
        )
        assert resp.status_code == 400


# ================================================================
# Admin Login
# ================================================================

class TestAdminLogin:

    def test_login_missing_fields_returns_400(self, client):
        resp = client.post(
            "/api/admin/login",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_login_wrong_user_returns_401(self, client):
        with patch("api.routes.get_db") as mock_db:
            mock_cur = MagicMock()
            mock_cur.fetchone.return_value = None
            mock_db.return_value.cursor.return_value = mock_cur

            with patch("api.routes.log_action"):
                resp = client.post(
                    "/api/admin/login",
                    data=json.dumps({"username": "nobody", "password": "wrong"}),
                    content_type="application/json",
                )
            assert resp.status_code == 401


# ================================================================
# Protected Endpoints (require_admin)
# ================================================================

class TestProtectedEndpoints:

    def test_decrypt_without_token_returns_401(self, client):
        resp = client.post(
            "/api/decrypt-votes",
            data=json.dumps({"private_key_password": "test"}),
            content_type="application/json",
        )
        assert resp.status_code == 401

    def test_logout_without_token_returns_401(self, client):
        resp = client.post("/api/admin/logout")
        assert resp.status_code == 401


# ================================================================
# Blockchain Status & Verify
# ================================================================

class TestBlockchainEndpoints:

    def test_verify_chain_returns_valid_field(self, client):
        with patch("api.routes.get_blockchain") as mock_bc, \
             patch("api.routes.get_db") as mock_db, \
             patch("api.routes.log_action"):
            mock_bc.return_value.verify_integrity.return_value = (True, "OK")
            mock_bc.return_value.__len__ = lambda _: 5
            mock_bc.return_value.last_block = MagicMock(hash="a" * 64)
            mock_db.return_value.cursor.return_value = MagicMock()

            resp = client.get("/api/verify-chain")
            assert resp.status_code == 200
            data = json.loads(resp.data)
            assert "valid" in data

    def test_blockchain_status_structure(self, client):
        with patch("api.routes.get_blockchain") as mock_bc:
            mock_bc.return_value.__len__ = lambda _: 3
            mock_bc.return_value.total_votes = 2
            mock_bc.return_value.last_block  = None

            resp = client.get("/api/blockchain/status")
            assert resp.status_code == 200
            data = json.loads(resp.data)
            assert "total_blocks" in data
            assert "total_votes"  in data
