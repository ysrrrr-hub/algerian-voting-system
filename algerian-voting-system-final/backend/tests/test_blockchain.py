"""
backend/tests/test_blockchain.py
اختبارات وحدة محرك البلوكشين (بدون قاعدة بيانات)
"""

import hashlib
import json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from blockchain.block import Block


# ================================================================ Block Tests
class TestBlock:

    def _make_block(self, index=1, encrypted_vote="enc_vote_data",
                    previous_hash="a" * 64):
        return Block(
            index=index,
            timestamp=datetime(2026, 7, 5, 10, 0, 0, tzinfo=timezone.utc),
            encrypted_vote=encrypted_vote,
            previous_hash=previous_hash,
        )

    def test_hash_is_64_chars(self):
        b = self._make_block()
        assert len(b.hash) == 64

    def test_hash_is_hexadecimal(self):
        b = self._make_block()
        int(b.hash, 16)  # يرفع ValueError إذا لم يكن hex

    def test_hash_changes_when_vote_tampered(self):
        b = self._make_block()
        original_hash = b.hash
        b.encrypted_vote = "tampered_data"
        assert b.calculate_hash() != original_hash

    def test_hash_changes_when_index_tampered(self):
        b = self._make_block()
        original_hash = b.hash
        b.index = 999
        assert b.calculate_hash() != original_hash

    def test_hash_deterministic(self):
        """نفس البيانات → نفس الـ hash دائماً"""
        b1 = self._make_block()
        b2 = self._make_block()
        assert b1.hash == b2.hash

    def test_to_dict_has_required_keys(self):
        b = self._make_block()
        d = b.to_dict()
        for key in ("index", "timestamp", "encrypted_vote",
                    "previous_hash", "current_hash", "nonce"):
            assert key in d

    def test_equality(self):
        b1 = self._make_block()
        b2 = self._make_block()
        assert b1 == b2

    def test_genesis_previous_hash_is_zeros(self):
        genesis = Block(
            index=0,
            timestamp=datetime.now(timezone.utc),
            encrypted_vote="GENESIS_BLOCK",
            previous_hash="0" * 64,
        )
        assert genesis.previous_hash == "0" * 64
        assert len(genesis.hash) == 64


# ================================================================ Blockchain Tests
class TestBlockchainIntegrity:
    """
    اختبارات سلامة السلسلة بدون DB (باستخدام Mock).
    """

    def _build_chain_obj(self):
        """بناء Blockchain مع Mock لقاعدة البيانات."""
        from blockchain.chain import Blockchain

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value = mock_cursor

        with patch.object(Blockchain, "_save_block_to_db"):
            bc = Blockchain.__new__(Blockchain)
            bc.db    = mock_conn
            bc.chain = []
            # إنشاء Genesis Block يدوياً
            genesis = Block(
                index=0,
                timestamp=datetime(2026, 7, 5, tzinfo=timezone.utc),
                encrypted_vote="GENESIS_BLOCK",
                previous_hash="0" * 64,
            )
            bc.chain.append(genesis)
        return bc

    def _add_dummy_block(self, bc):
        prev  = bc.chain[-1]
        block = Block(
            index=len(bc.chain),
            timestamp=datetime.now(timezone.utc),
            encrypted_vote=f"enc_{len(bc.chain)}",
            previous_hash=prev.hash,
        )
        bc.chain.append(block)
        return block

    def test_genesis_only_is_valid(self):
        bc = self._build_chain_obj()
        valid, msg = bc.verify_integrity()
        assert valid is True

    def test_three_linked_blocks_valid(self):
        bc = self._build_chain_obj()
        self._add_dummy_block(bc)
        self._add_dummy_block(bc)
        valid, msg = bc.verify_integrity()
        assert valid is True

    def test_tampered_vote_detected(self):
        bc = self._build_chain_obj()
        self._add_dummy_block(bc)
        # تلاعب
        bc.chain[1].encrypted_vote = "MALICIOUS_VOTE"
        valid, msg = bc.verify_integrity()
        assert valid is False
        assert "1" in msg  # يجب أن يشير لـ Block 1

    def test_broken_link_detected(self):
        bc = self._build_chain_obj()
        self._add_dummy_block(bc)
        self._add_dummy_block(bc)
        # كسر الرابط
        bc.chain[2].previous_hash = "b" * 64
        valid, msg = bc.verify_integrity()
        assert valid is False

    def test_total_votes_excludes_genesis(self):
        bc = self._build_chain_obj()
        assert bc.total_votes == 0
        self._add_dummy_block(bc)
        assert bc.total_votes == 1
        self._add_dummy_block(bc)
        assert bc.total_votes == 2

    def test_len_includes_genesis(self):
        bc = self._build_chain_obj()
        assert len(bc) == 1
        self._add_dummy_block(bc)
        assert len(bc) == 2
