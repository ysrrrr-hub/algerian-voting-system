#!/usr/bin/env python3
import psycopg

conn = psycopg.connect('dbname=voting_system user=voting_admin password=StrongPassword@2026 host=127.0.0.1')
cur = conn.cursor()

# Check if stored function exists
cur.execute("SELECT routine_name FROM information_schema.routines WHERE routine_name='check_voter_eligibility'")
funcs = cur.fetchall()
print(f'Function exists: {len(funcs) > 0}')

# Check voters table structure
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='voters' ORDER BY ordinal_position")
cols = [r[0] for r in cur.fetchall()]
print(f'Voters columns: {cols}')

# Check test voter
cur.execute("SELECT * FROM voters WHERE nfc_uid='04A1B2C3D4E5F6'")
row = cur.fetchone()
print(f'Test voter row: {row}')

conn.close()
