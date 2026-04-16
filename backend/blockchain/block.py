import hashlib
import json
from datetime import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key

class Block:
    def __init__(self, index, timestamp, encrypted_vote, previous_hash, nonce=0):
        self.index = index
        self.timestamp = timestamp
        self.encrypted_vote = encrypted_vote  # JSON مشفر: {"candidate_id": X, "nfc_uid": "..."}
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()
    
    def to_dict(self):
        """تحويل الكتلة إلى dictionary"""
        return {
            "index": self.index,
            "timestamp": self.timestamp.isoformat(timespec='seconds'),
            "encrypted_vote": self.encrypted_vote,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "nonce": self.nonce
        }
    
    def calculate_hash(self):
        """حساب SHA-256 للكتلة"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp.isoformat(timespec='seconds'),
            "encrypted_vote": self.encrypted_vote,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    @staticmethod
    def encrypt_vote(vote_data, public_key_path):
        """تشفير الصوت بالمفتاح العام"""
        try:
            with open(public_key_path, 'rb') as key_file:
                public_key = load_pem_public_key(key_file.read())
            
            vote_json = json.dumps(vote_data).encode()
            
            encrypted = public_key.encrypt(
                vote_json,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return encrypted.hex()  # تحويل لـ hexadecimal للتخزين
        except Exception as e:
            print(f"Error encrypting vote: {e}")
            raise
