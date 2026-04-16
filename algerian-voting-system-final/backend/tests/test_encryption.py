"""
backend/tests/test_encryption.py
اختبارات التشفير RSA-4096 + SHA-256
تعمل مع مفاتيح مؤقتة تُولَّد وقت الاختبار
"""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from blockchain.block import Block


# ================================================================
# Fixture: مفاتيح RSA-2048 مؤقتة (أسرع من 4096 في الاختبارات)
# ================================================================

@pytest.fixture(scope="module")
def rsa_keypair(tmp_path_factory):
    """
    يُولّد زوج مفاتيح RSA-2048 مؤقتاً لأغراض الاختبار فقط.
    في الإنتاج يُستخدم RSA-4096.
    """
    tmp = tmp_path_factory.mktemp("keys")
    password = b"TestPass@2026"

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend(),
    )

    # حفظ المفتاح الخاص (مشفر بـ AES-256)
    private_path = str(tmp / "private.pem")
    with open(private_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password),
        ))

    # حفظ المفتاح العام
    public_path = str(tmp / "public.pem")
    with open(public_path, "wb") as f:
        f.write(private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ))

    return {
        "public_path":  public_path,
        "private_path": private_path,
        "password":     password.decode(),
    }


# ================================================================
# Encrypt / Decrypt Tests
# ================================================================

class TestRsaEncryption:

    def test_encrypt_returns_hex_string(self, rsa_keypair):
        vote = {"candidate_id": 3, "nfc_uid": "TEST_001"}
        result = Block.encrypt_vote(vote, rsa_keypair["public_path"])
        # يجب أن يكون hexadecimal
        assert isinstance(result, str)
        assert len(result) > 0
        int(result, 16)   # يرفع ValueError إذا لم يكن hex

    def test_decrypt_recovers_original_vote(self, rsa_keypair):
        original = {"candidate_id": 2, "nfc_uid": "TEST_002"}
        enc = Block.encrypt_vote(original, rsa_keypair["public_path"])
        dec = Block.decrypt_vote(
            enc,
            rsa_keypair["private_path"],
            rsa_keypair["password"],
        )
        assert dec["candidate_id"] == original["candidate_id"]
        assert dec["nfc_uid"]      == original["nfc_uid"]

    def test_different_votes_produce_different_ciphertext(self, rsa_keypair):
        """RSA-OAEP يُضيف عشوائية → نفس الصوت ينتج ciphertext مختلف"""
        vote = {"candidate_id": 1, "nfc_uid": "TEST_003"}
        enc1 = Block.encrypt_vote(vote, rsa_keypair["public_path"])
        enc2 = Block.encrypt_vote(vote, rsa_keypair["public_path"])
        assert enc1 != enc2   # OAEP هو احتمالي وليس حتمياً

    def test_wrong_password_raises_valueerror(self, rsa_keypair):
        vote = {"candidate_id": 4, "nfc_uid": "TEST_004"}
        enc  = Block.encrypt_vote(vote, rsa_keypair["public_path"])
        with pytest.raises(ValueError):
            Block.decrypt_vote(enc, rsa_keypair["private_path"], "WRONG_PASSWORD")

    def test_tampered_ciphertext_raises_valueerror(self, rsa_keypair):
        vote = {"candidate_id": 1, "nfc_uid": "TEST_005"}
        enc  = Block.encrypt_vote(vote, rsa_keypair["public_path"])
        # تلاعب: تغيير أول بايتين
        tampered = "ff00" + enc[4:]
        with pytest.raises(ValueError):
            Block.decrypt_vote(tampered, rsa_keypair["private_path"],
                               rsa_keypair["password"])

    def test_missing_candidate_id_raises_valueerror(self, rsa_keypair):
        with pytest.raises(ValueError, match="candidate_id"):
            Block.encrypt_vote({"nfc_uid": "TEST_006"}, rsa_keypair["public_path"])

    def test_missing_nfc_uid_raises_valueerror(self, rsa_keypair):
        with pytest.raises(ValueError, match="nfc_uid"):
            Block.encrypt_vote({"candidate_id": 1}, rsa_keypair["public_path"])

    def test_encrypted_vote_contains_voted_at_timestamp(self, rsa_keypair):
        """يجب أن يحتوي الصوت المفكوك على timestamp لمنع replay attacks"""
        vote = {"candidate_id": 5, "nfc_uid": "TEST_007"}
        enc  = Block.encrypt_vote(vote, rsa_keypair["public_path"])
        dec  = Block.decrypt_vote(enc, rsa_keypair["private_path"],
                                   rsa_keypair["password"])
        assert "voted_at" in dec


# ================================================================
# SHA-256 Hash Tests
# ================================================================

class TestSha256Hashing:
    from datetime import datetime, timezone

    def _block(self):
        from datetime import datetime, timezone
        from blockchain.block import Block
        return Block(
            index=1,
            timestamp=datetime(2026, 7, 5, 10, 0, tzinfo=timezone.utc),
            encrypted_vote="sample_enc_data",
            previous_hash="a" * 64,
        )

    def test_hash_length_is_64(self):
        b = self._block()
        assert len(b.hash) == 64

    def test_hash_is_lowercase_hex(self):
        b = self._block()
        assert b.hash == b.hash.lower()
        int(b.hash, 16)

    def test_hash_changes_on_any_field_change(self):
        b = self._block()
        original = b.hash
        fields = [
            ("index",          999),
            ("encrypted_vote", "modified"),
            ("previous_hash",  "b" * 64),
            ("nonce",          42),
        ]
        for attr, val in fields:
            b2 = self._block()
            setattr(b2, attr, val)
            assert b2.calculate_hash() != original, \
                f"Changing {attr} should change hash"

    def test_hash_is_deterministic(self):
        b1 = self._block()
        b2 = self._block()
        assert b1.hash == b2.hash
