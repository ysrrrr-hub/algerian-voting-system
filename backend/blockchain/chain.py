from .block import Block
from datetime import datetime, timezone
import json

class Blockchain:
    def __init__(self, db_connection):
        self.db = db_connection
        self.chain = []
        self.load_chain_from_db()
        
        # إنشاء الكتلة الأولى (Genesis Block) إذا لم توجد
        if len(self.chain) == 0:
            self.create_genesis_block()
    
    def __len__(self):
        return len(self.chain)
    
    def create_genesis_block(self):
        """إنشاء أول كتلة في السلسلة (إذا لم تكن موجودة)"""
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM blockchain WHERE block_index = 0")
        row = cursor.fetchone()
        count = row['cnt'] if row else 0
        cursor.close()
        
        if count > 0:
            # Genesis block already exists, load it instead
            self.load_chain_from_db()
            return
        
        genesis = Block(0, datetime.now(timezone.utc), "GENESIS_BLOCK", "0" * 64)
        self.chain.append(genesis)
        self.save_block_to_db(genesis)
    
    def add_vote(self, vote_data, public_key_path, commit=True):
        """إضافة صوت جديد"""
        # 1. تشفير الصوت
        encrypted_vote = Block.encrypt_vote(vote_data, public_key_path)
        
        # 2. إنشاء كتلة جديدة
        previous_block = self.chain[-1]
        new_block = Block(
            index=len(self.chain),
            timestamp=datetime.now(timezone.utc),
            encrypted_vote=encrypted_vote,
            previous_hash=previous_block.hash
        )
        
        # 3. Mining: Find nonce such that hash starts with '0000'
        target = '0000'
        while not new_block.hash.startswith(target):
            new_block.nonce += 1
            new_block.hash = new_block.calculate_hash()

        # 4. إضافة للسلسلة وقاعدة البيانات
        self.chain.append(new_block)
        self.save_block_to_db(new_block, commit=commit)
        
        return new_block.hash  # إرجاع الـ hash لتوليد QR Code
    
    def verify_integrity(self):
        """التحقق من سلامة السلسلة"""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            
            # فحص 1: هل الـ hash محسوب بشكل صحيح؟
            if current.hash != current.calculate_hash():
                return False, f"Block {i}: Hash mismatch"
            
            # فحص 2: هل الربط بالكتلة السابقة صحيح؟
            if current.previous_hash != previous.hash:
                return False, f"Block {i}: Chain broken"
        
        return True, "Blockchain is valid"
    
    def save_block_to_db(self, block, commit=True):
        """حفظ الكتلة في قاعدة البيانات"""
        cursor = self.db.cursor()
        # Save timestamp as naive UTC for consistent hash calculation
        ts_naive_utc = block.timestamp.astimezone(timezone.utc).replace(tzinfo=None) if block.timestamp.tzinfo else block.timestamp
        cursor.execute("""
            INSERT INTO blockchain (block_index, timestamp, encrypted_vote, previous_hash, current_hash, nonce)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (block.index, ts_naive_utc, block.encrypted_vote, block.previous_hash, block.hash, block.nonce))
        if commit:
            self.db.commit()
    
    def load_chain_from_db(self):
        """تحميل السلسلة من قاعدة البيانات عند بدء التشغيل"""
        cursor = self.db.cursor()
        try:
            cursor.execute("""
                SELECT block_index, timestamp, encrypted_vote, 
                       previous_hash, current_hash, nonce 
                FROM blockchain ORDER BY block_index ASC
            """)
            rows = cursor.fetchall()
            
            for row in rows:
                ts = row['timestamp']
                # Ensure timestamp is UTC-aware for consistent hashing
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                block = Block(
                    index=row['block_index'],
                    timestamp=ts,
                    encrypted_vote=row['encrypted_vote'],
                    previous_hash=row['previous_hash'],
                    nonce=row['nonce']
                )
                block.hash = row['current_hash']
                self.chain.append(block)
        except Exception as e:
            print(f"Error loading chain: {e}")
            self.db.rollback()

    def decrypt_all_votes(self, private_key_path, password):
        """فك تشفير جميع الأصوات في السلسلة (بعد إغلاق الانتخابات الرسمي)"""
        decrypted_votes = []
        
        for block in self.chain:
            # Skip genesis block
            if block.index == 0 or block.encrypted_vote == "GENESIS_BLOCK":
                continue
            
            try:
                # This will raise an exception if password is wrong
                vote_data = Block.decrypt_vote(
                    block.encrypted_vote,
                    private_key_path,
                    password
                )
                
                # Format to match expectations in routes.py
                decrypted_votes.append({
                    'block_index': block.index,
                    'block_hash': block.hash,
                    'timestamp': block.timestamp.isoformat() if hasattr(block.timestamp, 'isoformat') else str(block.timestamp),
                    'candidate_id': vote_data.get('candidate_id'),
                })
            except Exception as e:
                # Re-raise to be handled by routes.py (e.g. ValueError for wrong password)
                raise e
        
        return decrypted_votes
