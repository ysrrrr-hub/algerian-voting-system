from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

print('Generating RSA-4096 keys...')
private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
NEW_PASSWORD = b'ANIE@Algeria2026'

with open('/opt/algerian-voting-system/secure/private_key_encrypted.pem', 'wb') as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(NEW_PASSWORD)
    ))

with open('/opt/algerian-voting-system/secure/public_key.pem', 'wb') as f:
    f.write(private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))

print('SUCCESS! New password: ANIE@Algeria2026')
