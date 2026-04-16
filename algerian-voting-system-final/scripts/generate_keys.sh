#!/usr/bin/env bash
# scripts/generate_keys.sh
# توليد مفاتيح RSA-4096 وحدها (بدون إعداد كامل)
# الاستخدام: bash scripts/generate_keys.sh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SECURE_DIR="$ROOT_DIR/secure"

echo "========================================"
echo "  توليد مفاتيح RSA-4096"
echo "  Génération des clés RSA-4096"
echo "========================================"
echo ""

mkdir -p "$SECURE_DIR"

if [[ -f "$SECURE_DIR/public_key.pem" ]]; then
    echo "⚠️  المفاتيح موجودة بالفعل في $SECURE_DIR"
    read -p "هل تريد إعادة التوليد؟ [y/N] " -n 1 -r; echo
    [[ $REPLY =~ ^[Yy]$ ]] || exit 0
fi

read -rsp "كلمة مرور المفتاح الخاص (ستُستخدم لفك تشفير الأصوات بعد الانتخابات): " KEY_PASS
echo
read -rsp "تأكيد كلمة المرور: " KEY_PASS2
echo

[[ "$KEY_PASS" == "$KEY_PASS2" ]] || { echo "❌ كلمات المرور لا تتطابق"; exit 1; }
[[ ${#KEY_PASS} -ge 12 ]]        || { echo "❌ كلمة المرور قصيرة جداً (12 حرف كحد أدنى)"; exit 1; }

cd "$ROOT_DIR/backend"
[[ -f venv/bin/activate ]] && source venv/bin/activate

python3 -m utils.key_generator \
    --generate \
    --output-dir "$SECURE_DIR" \
    --password   "$KEY_PASS"

echo ""
echo "✅ المفاتيح جاهزة في: $SECURE_DIR"
echo ""
echo "  المفتاح العام  → $SECURE_DIR/public_key.pem"
echo "  المفتاح الخاص  → $SECURE_DIR/private_key_encrypted.pem"
echo ""
echo "⚠️  احتفظ بكلمة المرور في:"
echo "   • مكان فيزيائي آمن (ورقة، خزنة)"
echo "   • بعيد عن الحاسوب المتصل بالشبكة"
echo "   • نسخة احتياطية عند جهة رسمية"
echo ""
echo "بدون كلمة المرور لن تتمكن من فك تشفير الأصوات!"
