#!/usr/bin/env bash
# scripts/setup.sh
# سكريبت الإعداد التلقائي الكامل للمشروع
# الاستخدام: bash scripts/setup.sh

set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()    { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }
section() { echo -e "\n${GREEN}══════ $* ══════${NC}"; }

# ─── التحقق من المتطلبات ─────────────────────────────────────
section "فحص المتطلبات"
command -v python3  >/dev/null || error "Python 3.11+ مطلوب"
command -v psql     >/dev/null || error "PostgreSQL مطلوب"
command -v flutter  >/dev/null || warn  "Flutter غير موجود — تطبيق الكيوسك لن يُبنى"
command -v node     >/dev/null || warn  "Node.js غير موجود — Dashboard لن يُبنى"
command -v openssl  >/dev/null || error "OpenSSL مطلوب لتوليد المفاتيح"
info "جميع المتطلبات الأساسية موجودة ✓"

# ─── المتغيرات ───────────────────────────────────────────────
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DB_NAME="voting_system"
DB_USER="voting_admin"

section "إعداد المتغيرات"

if [[ ! -f "$ROOT_DIR/.env" ]]; then
    cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
    info "تم إنشاء .env من القالب"
    warn "يرجى تعديل .env قبل المتابعة (DB_PASSWORD, SECRET_KEY)"
    read -p "هل عدّلت .env؟ [y/N] " -n 1 -r; echo
    [[ $REPLY =~ ^[Yy]$ ]] || error "يرجى تعديل .env أولاً"
fi

source "$ROOT_DIR/.env"
[[ -z "${DB_PASSWORD:-}" ]] && error "DB_PASSWORD فارغ في .env"
[[ -z "${SECRET_KEY:-}"   ]] && error "SECRET_KEY فارغ في .env"

# ─── 1. قاعدة البيانات ───────────────────────────────────────
section "إعداد قاعدة البيانات"

sudo -u postgres psql -tc "SELECT 1 FROM pg_user WHERE usename='$DB_USER'" \
    | grep -q 1 || sudo -u postgres psql -c \
    "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
info "المستخدم $DB_USER جاهز ✓"

sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" \
    | grep -q 1 || sudo -u postgres psql -c \
    "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
info "قاعدة البيانات $DB_NAME جاهزة ✓"

export PGPASSWORD="$DB_PASSWORD"
psql -U "$DB_USER" -d "$DB_NAME" -f "$ROOT_DIR/backend/database/schema.sql"
psql -U "$DB_USER" -d "$DB_NAME" -f "$ROOT_DIR/backend/database/views_functions.sql"
psql -U "$DB_USER" -d "$DB_NAME" -f "$ROOT_DIR/backend/database/seed_data.sql"
info "Schema + Views + Seed data applied ✓"

# ─── 2. مفاتيح RSA-4096 ──────────────────────────────────────
section "توليد مفاتيح RSA-4096"

SECURE_DIR="$ROOT_DIR/secure"
mkdir -p "$SECURE_DIR"

if [[ -f "$SECURE_DIR/public_key.pem" ]]; then
    warn "المفاتيح موجودة بالفعل — تم التخطي"
else
    read -rsp "أدخل كلمة مرور المفتاح الخاص (ستُحتاج لفك تشفير النتائج): " KEY_PASS
    echo
    cd "$ROOT_DIR/backend"
    python3 -m utils.key_generator \
        --generate \
        --output-dir "$SECURE_DIR" \
        --password "$KEY_PASS"
    info "المفاتيح توليدها ✓"
    warn "⚠️  احفظ كلمة المرور في مكان آمن!"
fi

# ─── 3. Backend Python ───────────────────────────────────────
section "إعداد Backend"

cd "$ROOT_DIR/backend"
python3 -m venv venv
source venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
info "متطلبات Python مثبتة ✓"

# نسخ .env للـ backend
cp "$ROOT_DIR/.env" "$ROOT_DIR/backend/.env"
info "ملف .env منسوخ ✓"

# تشغيل الاختبارات
info "تشغيل الاختبارات..."
pytest tests/ -q --tb=short && info "جميع الاختبارات نجحت ✓" \
    || warn "بعض الاختبارات فشلت — راجع الأخطاء"

deactivate

# ─── 4. React Dashboard ──────────────────────────────────────
section "إعداد Dashboard"

if command -v node >/dev/null; then
    cd "$ROOT_DIR/dashboard"
    npm install --silent
    info "متطلبات Node.js مثبتة ✓"
    info "لتشغيل Dashboard: cd dashboard && npm start"
else
    warn "Node.js غير موجود — تخطي Dashboard"
fi

# ─── 5. Flutter Kiosk ────────────────────────────────────────
section "إعداد Flutter Kiosk"

if command -v flutter >/dev/null; then
    cd "$ROOT_DIR/kiosk_app"
    flutter pub get --suppress-analytics
    info "متطلبات Flutter مثبتة ✓"
    info "لتشغيل الكيوسك: cd kiosk_app && flutter run"
else
    warn "Flutter غير موجود — تخطي Kiosk App"
fi

# ─── ملخص ────────────────────────────────────────────────────
section "✅ الإعداد اكتمل"
echo ""
echo "  🗄️  قاعدة البيانات : $DB_NAME@localhost:5432"
echo "  🔑  المفاتيح       : $SECURE_DIR"
echo ""
echo "  لتشغيل Backend:"
echo "    cd backend && source venv/bin/activate && python run.py"
echo ""
echo "  لتشغيل Dashboard:"
echo "    cd dashboard && npm start"
echo ""
echo "  لتشغيل الكيوسك:"
echo "    cd kiosk_app && flutter run -d linux"
echo ""
echo "  أو Docker:"
echo "    docker-compose up -d"
echo ""
