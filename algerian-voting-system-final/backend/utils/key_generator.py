"""
backend/utils/key_generator.py
RSA-4096 Key Generator — توليد وإدارة مفاتيح التشفير

يُنفَّذ مرة واحدة فقط قبل بدء الانتخابات:
    python -m utils.key_generator --generate --password "كلمة_مرور_قوية"

⚠️  تحذير: المفتاح الخاص يجب أن يُحفظ في مكان آمن ومعزول.
"""

import argparse
import os
import sys

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_rsa_4096(
    output_dir: str,
    password:   str,
) -> tuple[str, str]:
    """
    توليد زوج مفاتيح RSA-4096.

    Args:
        output_dir : مجلد حفظ المفاتيح (يُفضّل خارج المستودع)
        password   : كلمة مرور لتشفير المفتاح الخاص بـ AES-256

    Returns:
        (public_key_path, private_key_path)
    """
    os.makedirs(output_dir, exist_ok=True)

    print("⏳ Generating RSA-4096 keypair (this may take ~10s)...")

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend(),
    )

    # ─── المفتاح الخاص (مشفر بـ AES-256-CBC) ───────────────────
    private_path = os.path.join(output_dir, "private_key_encrypted.pem")
    with open(private_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(
                password.encode("utf-8")
            ),
        ))
    os.chmod(private_path, 0o600)   # قراءة/كتابة للمالك فقط

    # ─── المفتاح العام (غير مشفر) ─────────────────────────────
    public_path = os.path.join(output_dir, "public_key.pem")
    with open(public_path, "wb") as f:
        f.write(private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ))
    os.chmod(public_path, 0o644)

    print(f"✅ Public key  → {public_path}")
    print(f"✅ Private key → {private_path}  (AES-256 encrypted)")
    print(
        "\n⚠️  احتفظ بكلمة المرور في مكان آمن. "
        "بدونها لن تتمكن من فك تشفير الأصوات.\n"
    )

    return public_path, private_path


def verify_keypair(
    public_path:  str,
    private_path: str,
    password:     str,
) -> bool:
    """
    التحقق من تطابق المفتاحين عبر تشفير/فك تشفير بيانات وهمية.

    Returns:
        True إذا تطابق المفتاحان
    """
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import hashes
    import secrets

    test_data = secrets.token_bytes(32)

    try:
        # تحميل المفتاحين
        with open(public_path, "rb")  as f: pub_pem  = f.read()
        with open(private_path, "rb") as f: priv_pem = f.read()

        pub_key  = serialization.load_pem_public_key(pub_pem, backend=default_backend())
        priv_key = serialization.load_pem_private_key(
            priv_pem, password=password.encode(), backend=default_backend()
        )

        # تشفير ثم فك تشفير
        encrypted  = pub_key.encrypt(
            test_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        decrypted = priv_key.decrypt(
            encrypted,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        match = test_data == decrypted
        if match:
            print("✅ Keypair verification: PASSED")
        else:
            print("❌ Keypair verification: FAILED")
        return match

    except Exception as exc:
        print(f"❌ Keypair verification failed: {exc}")
        return False


# ─── CLI ────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="RSA-4096 Key Generator for Algerian Voting System"
    )
    parser.add_argument("--generate", action="store_true",
                        help="توليد زوج مفاتيح جديد")
    parser.add_argument("--verify", action="store_true",
                        help="التحقق من صحة المفاتيح الموجودة")
    parser.add_argument("--output-dir", default="../secure",
                        help="مجلد حفظ المفاتيح (افتراضي: ../secure)")
    parser.add_argument("--password", required=True,
                        help="كلمة مرور تشفير المفتاح الخاص")
    parser.add_argument("--public-key",
                        default="../secure/public_key.pem")
    parser.add_argument("--private-key",
                        default="../secure/private_key_encrypted.pem")

    args = parser.parse_args()

    if args.generate:
        generate_rsa_4096(args.output_dir, args.password)

    if args.verify:
        verify_keypair(args.public_key, args.private_key, args.password)

    if not args.generate and not args.verify:
        parser.print_help()
