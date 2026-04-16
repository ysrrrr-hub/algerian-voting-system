"""
backend/blockchain/chain.py
Blockchain Class — يدير سلسلة الكتل الكاملة

المسؤوليات:
  1. إنشاء Genesis Block (الكتلة الأولى)
  2. إضافة أصوات مشفرة كـ كتل جديدة
  3. التحقق من سلامة السلسلة (كشف أي تلاعب)
  4. فك تشفير جميع الأصوات بعد الانتخابات
  5. مزامنة الكتل مع قاعدة بيانات PostgreSQL
"""

import psycopg2
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from .block import Block


class Blockchain:
    """
    سلسلة البلوكشين التي تخزن جميع الأصوات المشفرة.

    آلية ضمان النزاهة:
      - كل كتلة تحمل hash الكتلة السابقة (previous_hash)
      - تغيير أي بيانات في أي كتلة يكسر السلسلة
      - verify_integrity() يكشف أي تلاعب في O(n)
    """

    def __init__(self, db_connection: psycopg2.extensions.connection) -> None:
        self.db = db_connection
        self.chain: List[Block] = []
        # تحميل السلسلة الموجودة من قاعدة البيانات
        self._load_chain_from_db()
        # إنشاء Genesis Block إذا كانت السلسلة فارغة
        if not self.chain:
            self._create_genesis_block()

    # ============================================================ Genesis
    def _create_genesis_block(self) -> Block:
        """
        إنشاء الكتلة الأولى في السلسلة.

        خصائصها الثابتة:
          index          = 0
          previous_hash  = "000...0" (64 صفراً — لا توجد كتلة سابقة)
          encrypted_vote = "GENESIS_BLOCK"
        """
        genesis = Block(
            index=0,
            timestamp=datetime.now(timezone.utc),
            encrypted_vote="GENESIS_BLOCK",
            previous_hash="0" * 64,
        )
        self.chain.append(genesis)
        self._save_block_to_db(genesis)
        print("✅ Genesis Block created")
        return genesis

    # ============================================================ Add vote
    def add_vote(
        self,
        vote_data: Dict[str, Any],
        public_key_path: str,
    ) -> str:
        """
        إضافة صوت جديد للبلوكشين.

        الخطوات:
          1. تشفير الصوت بـ RSA-4096
          2. جلب hash آخر كتلة (للربط)
          3. إنشاء كتلة جديدة وحساب SHA-256 hash
          4. حفظ في الذاكرة + قاعدة البيانات

        Returns:
            str — SHA-256 hash الكتلة الجديدة (يُستخدم كإيصال QR)
        """
        encrypted_vote = Block.encrypt_vote(vote_data, public_key_path)
        previous_block = self.chain[-1]

        new_block = Block(
            index=len(self.chain),
            timestamp=datetime.now(timezone.utc),
            encrypted_vote=encrypted_vote,
            previous_hash=previous_block.hash,
        )

        self.chain.append(new_block)
        self._save_block_to_db(new_block)

        print(
            f"✅ Block #{new_block.index} added | "
            f"hash={new_block.hash[:16]}…"
        )
        return new_block.hash

    # ============================================================ Verify
    def verify_integrity(self) -> Tuple[bool, str]:
        """
        التحقق من سلامة السلسلة بالكامل — O(n).

        لكل كتلة يُجري فحصين:
          1. إعادة حساب hash والمقارنة بالمخزّن
             (يكشف تعديل أي حقل في الكتلة)
          2. مقارنة previous_hash بـ hash الكتلة السابقة
             (يكشف إضافة/حذف كتل أو اختلال التسلسل)

        Returns:
            (True,  رسالة نجاح) أو (False, وصف الخلل)
        """
        if len(self.chain) <= 1:
            return True, "Blockchain is valid (genesis block only)"

        for i in range(1, len(self.chain)):
            current  = self.chain[i]
            previous = self.chain[i - 1]

            # فحص 1 — سلامة hash الكتلة الحالية
            recalculated = current.calculate_hash()
            if current.hash != recalculated:
                return False, (
                    f"Block {i}: hash mismatch! "
                    f"stored={current.hash[:16]}… "
                    f"calculated={recalculated[:16]}…"
                )

            # فحص 2 — سلامة الربط بالكتلة السابقة
            if current.previous_hash != previous.hash:
                return False, (
                    f"Block {i}: chain broken! "
                    f"expected_prev={previous.hash[:16]}… "
                    f"got={current.previous_hash[:16]}…"
                )

        return True, (
            f"Blockchain is valid "
            f"({len(self.chain)} blocks verified ✓)"
        )

    # ============================================================ Decrypt all
    def decrypt_all_votes(
        self,
        private_key_path: str,
        password: str,
    ) -> List[Dict[str, Any]]:
        """
        فك تشفير جميع الأصوات (للفرز بعد الانتخابات).

        يتخطى Genesis Block (index=0).

        Returns:
            [{'candidate_id', 'nfc_uid', 'voted_at', 'block_index', ...}]
        """
        results: List[Dict[str, Any]] = []
        failed = 0

        for block in self.chain[1:]:
            try:
                vote = Block.decrypt_vote(
                    block.encrypted_vote,
                    private_key_path,
                    password,
                )
                vote["block_index"] = block.index
                vote["timestamp"]   = block.timestamp.isoformat()
                vote["block_hash"]  = block.hash
                results.append(vote)
            except Exception as exc:
                failed += 1
                print(f"⚠️  Block {block.index} decryption failed: {exc}")

        print(
            f"✅ Decrypted {len(results)} votes "
            f"({failed} failed)"
        )
        return results

    # ============================================================ Results
    def get_results(
        self,
        private_key_path: str,
        password: str,
    ) -> Dict[int, int]:
        """
        حساب عدد الأصوات لكل مرشح.

        Returns:
            {candidate_id: vote_count}
        """
        votes = self.decrypt_all_votes(private_key_path, password)
        tally: Dict[int, int] = {}
        for v in votes:
            cid = v["candidate_id"]
            tally[cid] = tally.get(cid, 0) + 1
        return tally

    # ============================================================ DB helpers
    def _save_block_to_db(self, block: Block) -> None:
        """حفظ كتلة في جدول blockchain."""
        cursor = self.db.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO blockchain
                    (block_index, timestamp, encrypted_vote,
                     previous_hash, current_hash, nonce)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (block_index) DO NOTHING
                """,
                (
                    block.index,
                    block.timestamp,
                    block.encrypted_vote,
                    block.previous_hash,
                    block.hash,
                    block.nonce,
                ),
            )
            self.db.commit()
        finally:
            cursor.close()

    def _load_chain_from_db(self) -> None:
        """تحميل السلسلة الكاملة من قاعدة البيانات عند بدء التشغيل."""
        cursor = self.db.cursor()
        try:
            cursor.execute(
                """
                SELECT block_index, timestamp, encrypted_vote,
                       previous_hash, current_hash, nonce
                FROM blockchain
                ORDER BY block_index ASC
                """
            )
            rows = cursor.fetchall()
        finally:
            cursor.close()

        for row in rows:
            # دعم كل من dict (RealDictCursor) وtuple
            if isinstance(row, dict):
                idx, ts, ev = row["block_index"], row["timestamp"], row["encrypted_vote"]
                ph, ch, nc  = row["previous_hash"], row["current_hash"], row["nonce"]
            else:
                idx, ts, ev, ph, ch, nc = row

            block = Block(
                index=idx,
                timestamp=ts if isinstance(ts, datetime)
                          else datetime.fromisoformat(str(ts)),
                encrypted_vote=ev,
                previous_hash=ph,
                nonce=nc or 0,
            )
            # استخدام الـ hash المخزّن — لا نُعيد حسابه
            block.hash = ch
            self.chain.append(block)

        if self.chain:
            print(f"✅ Loaded {len(self.chain)} blocks from database")

    # ============================================================ Properties
    @property
    def last_block(self) -> Optional[Block]:
        return self.chain[-1] if self.chain else None

    @property
    def total_votes(self) -> int:
        """عدد الأصوات الفعلية (السلسلة ناقص Genesis Block)."""
        return max(0, len(self.chain) - 1)

    def __len__(self) -> int:
        return len(self.chain)

    def __repr__(self) -> str:
        last = self.chain[-1].hash[:16] if self.chain else "N/A"
        return (
            f"Blockchain(blocks={len(self.chain)}, "
            f"votes={self.total_votes}, "
            f"last={last}…)"
        )
