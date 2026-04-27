import re
import shutil
import os

BACKEND = '/opt/algerian-voting-system/backend'
CHAIN_FILE = f'{BACKEND}/blockchain/chain.py'
BLOCK_FILE = f'{BACKEND}/blockchain/block.py'

# Backup
shutil.copy(CHAIN_FILE, CHAIN_FILE + '.backup')
shutil.copy(BLOCK_FILE, BLOCK_FILE + '.backup')
print('Backups created')

# === 1. Add decrypt_vote to Block class ===
DECRYPT_VOTE_METHOD = '''
    @staticmethod
    def decrypt_vote(encrypted_hex, private_key_path, password):
        '''
        '''?? ????? ??? ???? ???????? ?????'''
        '''
        from cryptography.hazmat.primitives.serialization import load_pem_private_key
        try:
            with open(private_key_path, 'rb') as key_file:
                private_key = load_pem_private_key(
                    key_file.read(),
                    password=password.encode() if isinstance(password, str) else password
                )
            encrypted_bytes = bytes.fromhex(encrypted_hex)
            decrypted = private_key.decrypt(
                encrypted_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return json.loads(decrypted.decode())
        except Exception as e:
            print(f'Error decrypting vote: {e}')
            raise
'''

with open(BLOCK_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

if 'def decrypt_vote' not in content:
    # Insert before last line of file (assuming class ends at end of file)
    content = content.rstrip() + '\n' + DECRYPT_VOTE_METHOD + '\n'
    with open(BLOCK_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Added decrypt_vote to Block class')
else:
    print('decrypt_vote already exists in Block')

# === 2. Add decrypt_all_votes to Blockchain class ===
DECRYPT_ALL_METHOD = '''
    def decrypt_all_votes(self, private_key_path, password):
        '''
        '''?? ????? ???? ??????? ?? ??????? (??? ????? ??????????)'''
        '''
        decrypted_votes = []
        counts_by_candidate = {}
        total = 0
        errors = 0
        
        for block in self.chain:
            # Skip genesis block
            if block.index == 0:
                continue
            if block.encrypted_vote == 'GENESIS_BLOCK':
                continue
            
            try:
                vote = Block.decrypt_vote(block.encrypted_vote, private_key_path, password)
                cid = vote.get('candidate_id')
                decrypted_votes.append({
                    'block_index': block.index,
                    'timestamp': block.timestamp.isoformat() if hasattr(block.timestamp, 'isoformat') else str(block.timestamp),
                    'candidate_id': cid,
                })
                if cid is not None:
                    counts_by_candidate[cid] = counts_by_candidate.get(cid, 0) + 1
                total += 1
            except Exception as e:
                errors += 1
                print(f'Error decrypting block {block.index}: {e}')
                continue
        
        return {
            'success': True,
            'total_votes': total,
            'errors': errors,
            'votes': decrypted_votes,
            'results': counts_by_candidate,
            'counts_by_candidate': counts_by_candidate,
        }
'''

with open(CHAIN_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

if 'def decrypt_all_votes' not in content:
    content = content.rstrip() + '\n' + DECRYPT_ALL_METHOD + '\n'
    with open(CHAIN_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Added decrypt_all_votes to Blockchain class')
else:
    print('decrypt_all_votes already exists in Blockchain')

print('PATCH COMPLETE!')
