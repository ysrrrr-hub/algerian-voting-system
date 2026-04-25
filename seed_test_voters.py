#!/usr/bin/env python3
import psycopg

conn = psycopg.connect('dbname=voting_system user=voting_admin password=StrongPassword@2026 host=127.0.0.1')
cur = conn.cursor()

test_voters = [
    ('04A1B2C3D4E5F6', 'Ahmed', 'Ben Ali'),
    ('04B2C3D4E5F6A1', 'Fatima', 'Bouaziz'),
    ('04C3D4E5F6A1B2', 'Mohamed', 'Kasmi'),
]

for uid, fname, lname in test_voters:
    cur.execute('SELECT nfc_uid FROM voters WHERE nfc_uid=%s', (uid,))
    if not cur.fetchone():
        cur.execute(
            'INSERT INTO voters (nfc_uid, first_name, last_name, has_voted, wilaya) VALUES (%s, %s, %s, false, 16)',
            (uid, fname, lname)
        )
        print(f'Added: {fname} {lname} ({uid})')
    else:
        print(f'Exists: {fname} {lname} ({uid})')

conn.commit()
conn.close()
print('Done!')
