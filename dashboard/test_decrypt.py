import os
import sys
os.chdir('/opt/algerian-voting-system/backend')
sys.path.insert(0, '/opt/algerian-voting-system/backend')

from dotenv import load_dotenv
load_dotenv()

import psycopg
from blockchain.chain import Blockchain

conn = psycopg.connect(
    host='localhost',
    dbname='voting_system',
    user='voting_admin',
    password='StrongPassword@2026'
)
print('DB connected OK')

bc = Blockchain(conn)
print('Blockchain initialized OK')

print('--- Attempting decrypt ---')
try:
    votes = bc.decrypt_all_votes('/opt/algerian-voting-system/secure/private_key_encrypted.pem', 'ANIE@Algeria2026')
    print('SUCCESS! Decrypted votes:')
    print(votes)
except Exception as e:
    import traceback
    print('=== ERROR TRACEBACK ===')
    traceback.print_exc()
    print('=== END TRACEBACK ===')
