from .block import Block
from datetime import datetime
import psycopg2
import json

class Blockchain:
    def __init__(self, db_connection):
        self.db = db_connection
        self.chain = []
        self.load_chain_from_db()
        
        # إنشاء الكتلة الأولى (Genesis Block) إذا لم توجد
        if len(self.chain) == 0:
            self.create_genesis_block()
    
    def create_genesis_block(self):
        """إنشاء أول كتلة في السلسلة (إذا لم تكن موجودة)"""
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM blockchain WHERE block_index = 0")
        count = cursor.fetchone()[0]
        cursor.close()
        
        if count > 0:
            # Genesis block already exists, load it instead
            self.load_chain_from_db()
            return
        
        genesis = Block(0, datetime.now(), "GENESIS_BLOCK", "0")
        self.chain.append(genesis)
        self.save_block_to_db(genesis)
    
    def add_vote(self, vote_data, public_key_path):
        """إضافة صوت جديد"""
        # 1. تشفير الصوت
        encrypted_vote = Block.encrypt_vote(vote_data, public_key_path)
        
        # 2. إنشاء كتلة جديدة
        previous_block = self.chain[-1]
        new_block = Block(
            index=len(self.chain),
            timestamp=datetime.now(),
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
        self.save_block_to_db(new_block)
        
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
    
    def save_block_to_db(self, block):
        """حفظ الكتلة في قاعدة البيانات"""
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO blockchain (block_index, timestamp, encrypted_vote, previous_hash, current_hash, nonce)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (block.index, block.timestamp, block.encrypted_vote, block.previous_hash, block.hash, block.nonce))
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
                block = Block(
                    index=row[0],
                    timestamp=row[1],
                    encrypted_vote=row[2],
                    previous_hash=row[3],
                    nonce=row[5]
                )
                block.hash = row[4]
                self.chain.append(block)
        except Exception as e:
            print(f"Error loading chain: {e}")
            self.db.rollback()
