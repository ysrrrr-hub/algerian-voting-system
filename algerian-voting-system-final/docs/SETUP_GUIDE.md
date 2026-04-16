# 🚀 دليل الإعداد والتشغيل
## Guide d'installation et de démarrage

---

## المتطلبات الأساسية

```bash
# التحقق من الإصدارات
python3 --version   # 3.11+
psql --version      # 15+
flutter --version   # 3.22+
node --version      # 20+
npm  --version      # 10+
openssl version     # 3.0+
```

---

## 1️⃣ إعداد قاعدة البيانات PostgreSQL

```bash
# إنشاء المستخدم وقاعدة البيانات
sudo -u postgres psql << EOF
CREATE USER voting_admin WITH PASSWORD 'StrongPassword@2026';
CREATE DATABASE voting_system OWNER voting_admin;
GRANT ALL PRIVILEGES ON DATABASE voting_system TO voting_admin;
EOF

# تطبيق الـ Schema
psql -U voting_admin -d voting_system \
     -f backend/database/schema.sql

# إنشاء الـ Views والدوال المخزنة
psql -U voting_admin -d voting_system \
     -f backend/database/views_functions.sql

# بيانات تجريبية (للتطوير فقط)
psql -U voting_admin -d voting_system \
     -f backend/database/seed_data.sql
```

---

## 2️⃣ توليد مفاتيح RSA-4096

```bash
# إنشاء مجلد المفاتيح (خارج المستودع!)
mkdir -p secure

# توليد المفاتيح عبر السكريبت
cd backend
python -m utils.key_generator \
       --generate \
       --output-dir ../secure \
       --password "كلمة_مرور_سرية_قوية_جداً"

# التحقق من صحة المفاتيح
python -m utils.key_generator \
       --verify \
       --public-key  ../secure/public_key.pem \
       --private-key ../secure/private_key_encrypted.pem \
       --password "كلمة_مرور_سرية_قوية_جداً"
```

> ⚠️ **تحذير:** احتفظ بكلمة المرور في مكان آمن منفصل.
> بدونها لن تتمكن من فك تشفير الأصوات بعد الانتخابات.

---

## 3️⃣ تشغيل Backend

```bash
cd backend

# إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# تثبيت المتطلبات
pip install -r requirements.txt

# نسخ وتعديل ملف البيئة
cp .env .env.local
nano .env.local   # عدّل DB_PASSWORD و SECRET_KEY

# تشغيل الخادم
python run.py

# ✅ سيعمل على: http://localhost:5000
# ✅ Health: http://localhost:5000/api/health
```

---

## 4️⃣ تشغيل Flutter Kiosk

```bash
cd kiosk_app

# تثبيت المتطلبات
flutter pub get

# تعديل عنوان API
# ← افتح: lib/core/utils/api_client.dart
# ← غيّر: static const String _base = 'http://IP_الخادم:5000/api';

# تشغيل (اختر المنصة المناسبة)
flutter run -d linux          # Linux kiosk
flutter run -d android        # Android tablet
flutter run -d chrome         # للتطوير فقط

# بناء للإنتاج
flutter build linux --release
flutter build apk --release
```

---

## 5️⃣ تشغيل React Dashboard

```bash
cd dashboard

# تثبيت المتطلبات
npm install

# تشغيل التطوير
npm start
# ✅ سيعمل على: http://localhost:3000

# بناء للإنتاج
npm run build
# يُنشئ مجلد build/ جاهز للرفع

# بيانات الدخول الافتراضية:
# Username: admin
# Password: Admin@2026
```

---

## 6️⃣ تشغيل الاختبارات

```bash
cd backend
source venv/bin/activate

# جميع الاختبارات
pytest tests/ -v

# مع تقرير التغطية
pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html

# اختبار محدد
pytest tests/test_blockchain.py -v
pytest tests/test_encryption.py -v
pytest tests/test_api.py -v
```

---

## 7️⃣ التحقق من صحة النظام

```bash
# فحص الـ API
curl http://localhost:5000/api/health

# جلب المرشحين
curl http://localhost:5000/api/candidates

# فحص ناخب تجريبي
curl http://localhost:5000/api/voter-status/TEST_VOTER_001

# التحقق من البلوكشين
curl http://localhost:5000/api/verify-chain

# الإحصائيات
curl http://localhost:5000/api/stats
```

---

## 🔧 استكشاف الأخطاء

| المشكلة | الحل |
|---------|------|
| `Connection refused :5000` | تأكد من تشغيل `python run.py` |
| `psycopg2 error` | تحقق من DB_PASSWORD في .env |
| `Public key not found` | نفّذ خطوة توليد المفاتيح أولاً |
| `Flutter: SocketException` | تحقق من عنوان `_base` في api_client.dart |
| `bcrypt error` | `pip install bcrypt==4.1.3` |
| `eventlet error` | `pip install eventlet==0.36.1` |

---

## 🔐 نقاط الأمان للإنتاج

```bash
# 1. تغيير كلمة مرور المشرف الافتراضية
psql -U voting_admin -d voting_system -c "
UPDATE admin_users
SET password_hash = '$2b$12$NEW_BCRYPT_HASH'
WHERE username = 'admin';
"

# 2. تقييد CORS
# في backend/.env:
ALLOWED_ORIGINS=http://192.168.1.50:3000

# 3. تعطيل وضع التطوير
FLASK_DEBUG=False

# 4. جدار الحماية (السماح فقط لـ kiosk و dashboard)
ufw allow from 192.168.1.0/24 to any port 5000
ufw deny 5000
```
