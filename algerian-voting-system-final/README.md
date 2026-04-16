# 🗳️ نظام التصويت الإلكتروني الجزائري
## Système de Vote Électronique Algérien — Blockchain 2026

> **تقنية:** Blockchain + SHA-256 + RSA-4096 + PostgreSQL + Flutter + React  
> **نمط:** Clean Architecture  
> **الهدف:** انتخابات رئاسية جزائرية 2026

---

## 🏗️ هيكل المشروع

```
algerian-voting-system/
├── backend/                ← Python / Flask
│   ├── blockchain/         ← Block + Blockchain (SHA-256 + RSA-4096)
│   ├── core/               ← Config + Exceptions
│   ├── database/           ← Schema + Connection Pool
│   ├── api/                ← 10 REST endpoints + Middleware
│   ├── utils/              ← Audit + QR Generator
│   ├── tests/              ← Unit tests
│   ├── requirements.txt
│   └── run.py
├── kiosk_app/              ← Flutter (Clean Architecture)
│   └── lib/
│       ├── core/           ← Colors + Strings + Theme + API Client
│       ├── data/           ← Models + RemoteDataSource
│       ├── presentation/   ← Provider + 8 Screens + Widgets
│       └── main.dart
└── dashboard/              ← React + TypeScript + MUI + Recharts
    └── src/
        ├── services/       ← API layer
        ├── components/     ← StatsCard + BlockchainChart + IntegrityBadge
        └── pages/          ← Login + Dashboard + Results
```

---

## 🚀 تشغيل المشروع

### 1. قاعدة البيانات
```bash
sudo -u postgres psql -c "CREATE USER voting_admin WITH PASSWORD 'StrongPassword@2026';"
sudo -u postgres psql -c "CREATE DATABASE voting_system OWNER voting_admin;"
psql -U voting_admin -d voting_system -f backend/database/schema.sql
psql -U voting_admin -d voting_system -f backend/database/views_functions.sql
psql -U voting_admin -d voting_system -f backend/database/seed_data.sql
```

### 2. توليد مفاتيح RSA-4096
```bash
mkdir -p secure
openssl genrsa -aes256 -out secure/private_key_encrypted.pem 4096
openssl rsa -in secure/private_key_encrypted.pem -pubout -out secure/public_key.pem
```

### 3. Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env .env.local   # عدّل القيم
python run.py        # → http://localhost:5000
```

### 4. Flutter Kiosk
```bash
cd kiosk_app
flutter pub get
# عدّل lib/core/utils/api_client.dart → baseUrl
flutter run -d linux  # أو android / web
```

### 5. React Dashboard
```bash
cd dashboard
npm install
npm start   # → http://localhost:3000
```

---

## 🔐 آلية الأمان

| الطبقة | التقنية | الهدف |
|--------|---------|-------|
| التشفير | RSA-4096 + OAEP | حماية الصوت من القراءة |
| السلسلة | SHA-256 | كشف أي تلاعب فوري |
| المصادقة | bcrypt + JWT | حماية لوحة المشرفين |
| السجل | audit_log | تتبع كل إجراء |
| التصويت | has_voted flag | منع التصويت المزدوج |

---

## 📡 API Endpoints

| Method | Endpoint | الوصف |
|--------|----------|-------|
| GET | `/api/health` | فحص الصحة |
| POST | `/api/admin/login` | تسجيل دخول |
| GET | `/api/voter-status/:uid` | أهلية الناخب |
| GET | `/api/candidates` | قائمة المرشحين |
| POST | `/api/vote` | تسجيل صوت |
| GET | `/api/verify-chain` | التحقق من السلسلة |
| GET | `/api/blockchain/status` | حالة البلوكشين |
| GET | `/api/stats` | إحصائيات حية |
| POST | `/api/decrypt-votes` | فك التشفير (مشرفون) |

---

## 🧪 تشغيل الاختبارات
```bash
cd backend
pytest tests/ -v --cov=. --cov-report=term-missing
```

---

## 👥 بيانات تجريبية

| NFC UID | الاسم | الحالة |
|---------|-------|--------|
| TEST_VOTER_001 | ناخب تجريبي 1 | لم يصوّت بعد |
| TEST_VOTER_002 | ناخب تجريبي 2 | لم يصوّت بعد |

**بيانات المشرف:**  
- Username: `admin`  
- Password: `Admin@2026`
