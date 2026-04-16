import psycopg2
from datetime import datetime, timezone
import hashlib, json

conn = psycopg2.connect('host=localhost dbname=voting_system user=voting_admin password=StrongPassword@2026')
cur = conn.cursor()
cur.execute('SELECT block_index, timestamp, encrypted_vote, previous_hash, current_hash, nonce FROM blockchain ORDER BY block_index')
rows = cur.fetchall()

for row in rows:
    idx, ts, ev, ph, ch, nc = row
    print(f'=== Block {idx} ===')
    print(f'  DB timestamp type: {type(ts)}')
    print(f'  DB timestamp value: {repr(ts)}')
    print(f'  isoformat(): {ts.isoformat()}')
    print(f'  isoformat(timespec="seconds"): {ts.isoformat(timespec="seconds")}')

    # حساب hash بالطريقة الحالية في block.py
    d1 = {'index': idx, 'timestamp': ts.isoformat(timespec='seconds'), 'encrypted_vote': ev, 'previous_hash': ph, 'nonce': nc or 0}
    h1 = hashlib.sha256(json.dumps(d1, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

    # حساب hash بدون timespec
    d2 = {'index': idx, 'timestamp': ts.isoformat(), 'encrypted_vote': ev, 'previous_hash': ph, 'nonce': nc or 0}
    h2 = hashlib.sha256(json.dumps(d2, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

    print(f'  Stored hash:              {ch}')
    print(f'  Calculated (timespec=s):  {h1}')
    print(f'  Calculated (no timespec): {h2}')
    print(f'  Match timespec=s: {ch == h1}')
    print(f'  Match no timespec: {ch == h2}')
    print()

conn.close()
