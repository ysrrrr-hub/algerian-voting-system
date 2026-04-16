#!/usr/bin/env bash
# scripts/reset_voting.sh
# إعادة تعيين النظام ليوم انتخابي جديد
# ⚠️  خطر: يحذف جميع الأصوات والسجلات!

set -euo pipefail

echo "========================================"
echo "  ⚠️  إعادة تعيين نظام التصويت"
echo "  ⚠️  RÉINITIALISATION DU SYSTÈME"
echo "========================================"
echo ""
echo "هذا الإجراء سيحذف:"
echo "  • جميع الأصوات من البلوكشين"
echo "  • جميع سجلات التدقيق"  
echo "  • إعادة تعيين has_voted لجميع الناخبين"
echo ""
read -p "هل أنت متأكد؟ اكتب 'RESET' للتأكيد: " CONFIRM

[[ "$CONFIRM" == "RESET" ]] || { echo "❌ إلغاء العملية"; exit 0; }

# قراءة إعدادات قاعدة البيانات
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT_DIR/backend/.env" 2>/dev/null || source "$ROOT_DIR/.env"

export PGPASSWORD="$DB_PASSWORD"

echo ""
echo "⏳ جاري إعادة التعيين..."

psql -U "${DB_USER:-voting_admin}" -d "${DB_NAME:-voting_system}" << 'SQL'
BEGIN;

-- حذف جميع كتل البلوكشين عدا Genesis
DELETE FROM blockchain WHERE block_index > 0;

-- إعادة تعيين حالة التصويت
UPDATE voters SET has_voted = FALSE, voted_at = NULL;

-- حذف سجلات التدقيق
TRUNCATE audit_log;

-- حذف الجلسات المنتهية
DELETE FROM admin_sessions WHERE expires_at < NOW() OR is_revoked = TRUE;

COMMIT;
SQL

echo ""
echo "✅ تم إعادة التعيين بنجاح"
echo "  • البلوكشين: Genesis Block فقط"
echo "  • الناخبون: جاهزون للتصويت"
echo "  • سجل التدقيق: فارغ"
