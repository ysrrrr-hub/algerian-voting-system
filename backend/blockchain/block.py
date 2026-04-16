"""
backend/blockchain/block.py
Block Class — يمثل كتلة واحدة في سلسلة البلوكشين

كل كتلة تحتوي على:
  - index         : موقعها في السلسلة (0 = Genesis)
  - timestamp     : وقت إنشائها (UTC)
  - encrypted_vote: الصوت المشفر بـ RSA-4096 (hex string)
  - previous_hash : SHA-256 hash للكتلة السابقة (الربط)
  - nonce         : قيمة إضافية (Proof-of-Work مستقبلاً)
  - hash          : SHA-256 hash لهذه الكتلة (يُحسب تلقائياً)
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


class Block:
    """
    كتلة في سلسلة البلوكشين تحتوي على صوت واحد مشفر.

    خوارزميات التشفير:
        SHA-256    — حساب بصمة الكتلة
        RSA-4096   — تشفير/فك تشفير الصوت (OAEP + SHA-256)
    """

    # ------------------------------------------------------------------ init
    def __init__(
        self,
        index: int,
        timestamp: datetime,
        encrypted_vote: str,
        previous_hash: str,
        nonce: int = 0,
    ) -> None:
        self.index          = index
        self.timestamp      = timestamp
        self.encrypted_vote = encrypted_vote
        self.previous_hash  = previous_hash
        self.nonce          = nonce
        # البصمة تُحسب تلقائياً عند الإنشاء
        self.hash: str = self.calculate_hash()

    # ------------------------------------------------------------------ hash
    def calculate_hash(self) -> str:
        """
        حساب SHA-256 hash للكتلة.

        الخطوات:
          1. تجميع جميع حقول الكتلة في dictionary
          2. تحويلها لـ JSON مرتب (sort_keys=True) لضمان حتمية النتيجة
          3. حساب SHA-256 على النص الناتج (UTF-8)

        أي تغيير في أي حقل → hash مختلف تماماً → كشف التلاعب فوراً.

        Returns:
            hexadecimal string بطول 64 حرفاً (256 بت)
        """
        block_data = {
            "index":          self.index,
            "timestamp":      self.timestamp.isoformat(timespec='seconds'),
            "encrypted_vote": self.encrypted_vote,
            "previous_hash":  self.previous_hash,
            "nonce":          self.nonce,
        }
        raw = json.dumps(block_data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    # ------------------------------------------------------------------ encrypt
    @staticmethod
    def encrypt_vote(vote_data: Dict[str, Any], public_key_path: str) -> str:
        """
        تشفير بيانات الصوت بـ RSA-4096 + OAEP.

        Args:
            vote_data       : {'candidate_id': int, 'nfc_uid': str}
            public_key_path : مسار المفتاح العام (.pem)

        Returns:
            الصوت المشفر كـ hexadecimal string

        Raises:
            ValueError        : بيانات الصوت ناقصة
            FileNotFoundError : المفتاح غير موجود
        """
        if not vote_data.get("candidate_id"):
            raise ValueError("Missing candidate_id in vote data")
        if not vote_data.get("nfc_uid"):
            raise ValueError("Missing nfc_uid in vote data")

        # إضافة timestamp لمنع هجمات الإعادة (replay attacks)
        vote_data["voted_at"] = datetime.now(timezone.utc).isoformat()
        vote_json = json.dumps(vote_data, sort_keys=True).encode("utf-8")

        with open(public_key_path, "rb") as f:
            public_key = serialization.load_pem_public_key(
                f.read(), backend=default_backend()
            )

        encrypted = public_key.encrypt(
            vote_json,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return encrypted.hex()

    # ------------------------------------------------------------------ decrypt
    @staticmethod
    def decrypt_vote(
        encrypted_hex: str,
        private_key_path: str,
        password: str,
    ) -> Dict[str, Any]:
        """
        فك تشفير صوت باستخدام المفتاح الخاص.

        يُستدعى فقط بعد إغلاق باب التصويت لعدّ الأصوات.
        المفتاح الخاص محمي بكلمة مرور (AES-256).

        Args:
            encrypted_hex    : الصوت المشفر (hex string)
            private_key_path : مسار المفتاح الخاص المشفر
            password         : كلمة مرور المفتاح الخاص

        Returns:
            {'candidate_id': int, 'nfc_uid': str, 'voted_at': str}

        Raises:
            ValueError : فشل فك التشفير
        """
        try:
            with open(private_key_path, "rb") as f:
                private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=password.encode("utf-8"),
                    backend=default_backend(),
                )

            encrypted_bytes = bytes.fromhex(encrypted_hex)
            decrypted = private_key.decrypt(
                encrypted_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
            return json.loads(decrypted.decode("utf-8"))
        except Exception as exc:
            raise ValueError(f"Decryption failed: {exc}") from exc

    # ------------------------------------------------------------------ helpers
    def to_dict(self) -> Dict[str, Any]:
        """تحويل الكتلة لـ dictionary (للتخزين أو الإرسال عبر API)."""
        return {
            "index":         self.index,
            "timestamp":     self.timestamp.isoformat(timespec='seconds'),
            "encrypted_vote": self.encrypted_vote,
            "previous_hash": self.previous_hash,
            "current_hash":  self.hash,
            "nonce":         self.nonce,
        }

    def __repr__(self) -> str:
        return (
            f"Block(index={self.index}, "
            f"hash={self.hash[:16]}…, "
            f"prev={self.previous_hash[:16]}…)"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Block):
            return False
        return self.hash == other.hash
