import re

filepath = 'blockchain/chain.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# البحث عن الجزء القديم في _load_chain_from_db
old_code = 'block = Block(\n                index=idx,\n                timestamp=ts if isinstance(ts, datetime)\n                    else datetime.fromisoformat(str(ts)),\n                encrypted_vote=ev,\n                previous_hash=ph,\n                nonce=nc or 0,\n            )'

new_code = '''# تحويل timestamp لـ UTC timezone-aware datetime
                if isinstance(ts, datetime):
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=timezone.utc)
                else:
                    ts_str = str(ts)
                    ts = datetime.fromisoformat(ts_str)
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=timezone.utc)

                block = Block(
                    index=idx,
                    timestamp=ts,
                    encrypted_vote=ev,
                    previous_hash=ph,
                    nonce=nc or 0,
                )'''

if old_code in content:
    content = content.replace(old_code, new_code)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Fixed! (method 1)')
else:
    # الطريقة البديلة - استبدال بسيط
    old_simple = 'timestamp=ts if isinstance(ts, datetime)\n                    else datetime.fromisoformat(str(ts)),'
    new_simple = '''timestamp=ts.replace(tzinfo=timezone.utc) if isinstance(ts, datetime) and ts.tzinfo is None
                    else ts if isinstance(ts, datetime)
                    else datetime.fromisoformat(str(ts)).replace(tzinfo=timezone.utc),'''
    
    if old_simple in content:
        content = content.replace(old_simple, new_simple)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print('Fixed! (method 2)')
    else:
        print('Could not find the code to replace.')
        print('Trying direct fix...')
        
        # الحل المباشر - نعيد بناء _load_chain_from_db
        # نضمن أن كل timestamp يكون UTC
        content = content.replace(
            'timestamp=ts if isinstance(ts, datetime)',
            'timestamp=ts.replace(tzinfo=timezone.utc) if isinstance(ts, datetime) and ts.tzinfo is None\n                    else ts if isinstance(ts, datetime)'
        )
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print('Fixed! (method 3)')