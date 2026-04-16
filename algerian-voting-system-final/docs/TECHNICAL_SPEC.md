# 📋 المواصفة التقنية الشاملة
## Spécification Technique Complète
### نظام التصويت الإلكتروني الجزائري — 2026

---

## 1. نظرة معمارية عامة

```
┌─────────────────────────────────────────────────────────────┐
│                     Flutter Kiosk App                        │
│  Welcome → Language → NFC Scan → Verify → Candidates        │
│  → Confirm → Processing → Success / Error                    │
└─────────────────┬───────────────────────────────────────────┘
                  │  HTTP/REST  (JSON)
┌─────────────────▼───────────────────────────────────────────┐
│                  Flask REST API  :5000                        │
│  /api/health  /api/vote  /api/candidates  /api/stats  …      │
│                Socket.IO (:5000/ws)                          │
└──────┬──────────────────────────────────────┬───────────────┘
       │  psycopg2 (Pool)                      │  emit()
┌──────▼──────────────┐             ┌──────────▼──────────────┐
│    PostgreSQL 16     │             │   React Dashboard :3000  │
│  voters             │             │  Login → Dashboard       │
│  candidates         │             │  → Results               │
│  blockchain         │             └──────────────────────────┘
│  audit_log          │
│  admin_users        │
│  admin_sessions     │
│  encryption_keys    │
└─────────────────────┘
```

---

## 2. تدفق التصويت الكامل (Voting Flow)

```
Voter arrives at kiosk
        │
        ▼
[1] Welcome Screen
    └── زر "ابدأ التصويت" ──────────────────────────────►
                                                          │
[2] Language Selection (AR / FR)                         │
    └── اختيار اللغة ──────────────────────────────────►│
                                                          │
[3] NFC Scan Screen                                       │
    └── إدخال NFC UID                                     │
    └── GET /api/voter-status/{uid}                       │
         ├── 404 Not Found  ──► Error: Invalid Card       │
         ├── has_voted=True ──► Error: Already Voted      │
         └── eligible=True  ──► Continue ─────────────►  │
                                                          │
[4] Voter Verified Screen                                 │
    └── عرض اسم الناخب ────────────────────────────────► │
                                                          │
[5] Candidates Screen                                     │
    └── GET /api/candidates                               │
    └── عرض 5 بطاقات في Grid                              │
    └── اختيار مرشح → تفعيل زر التأكيد ─────────────►   │
                                                          │
[6] Confirmation Dialog                                   │
    └── عرض اسم المرشح + تحذير                            │
    └── "تأكيد" ──────────────────────────────────────►  │
                                                          │
[7] Processing Screen (animated)                          │
    ├── Step 1: تشفير RSA-4096                            │
    ├── Step 2: POST /api/vote                            │
    │           ├── check eligibility (DB)               │
    │           ├── validate candidate (DB)              │
    │           ├── Block.encrypt_vote() → hex           │
    │           ├── Blockchain.add_vote() → hash         │
    │           ├── UPDATE voters SET has_voted=TRUE     │
    │           ├── INSERT audit_log                     │
    │           └── emit("new_vote") via Socket.IO       │
    ├── Step 3: verify_integrity() pass                   │
    └── Step 4: generate_vote_qr(hash)                   │
                                                          │
[8] Success Screen                                        │
    ├── ✅ تم التصويت بنجاح                               │
    ├── QR Code (SHA-256 hash)                            │
    └── Countdown 30s → Welcome Screen                   │
```

---

## 3. بنية قاعدة البيانات

### جدول `voters`
| العمود | النوع | الوصف |
|--------|-------|-------|
| voter_id | SERIAL PK | معرف تلقائي |
| nfc_uid | VARCHAR(64) UNIQUE | معرف بطاقة NFC |
| full_name_ar | VARCHAR(255) | الاسم بالعربية |
| full_name_fr | VARCHAR(255) | الاسم بالفرنسية |
| date_of_birth | DATE | تاريخ الميلاد (≥18 سنة) |
| wilaya | VARCHAR(100) | الولاية |
| has_voted | BOOLEAN | هل صوّت؟ (منع التكرار) |
| voted_at | TIMESTAMP | وقت التصويت |

### جدول `blockchain`
| العمود | النوع | الوصف |
|--------|-------|-------|
| block_index | INT UNIQUE | موقع الكتلة (0=Genesis) |
| encrypted_vote | TEXT | الصوت مشفر RSA-4096 hex |
| previous_hash | VARCHAR(64) | hash الكتلة السابقة |
| current_hash | VARCHAR(64) UNIQUE | SHA-256 لهذه الكتلة |
| nonce | INT | للتوسع مستقبلاً |

### جدول `audit_log`
| العمود | النوع | الوصف |
|--------|-------|-------|
| action_type | VARCHAR(50) | VOTE_CAST / ADMIN_LOGIN / ... |
| nfc_uid | VARCHAR(64) | بطاقة الناخب |
| ip_address | VARCHAR(45) | IPv4 أو IPv6 |
| success | BOOLEAN | نجاح/فشل الإجراء |
| error_message | TEXT | تفاصيل الخطأ |

---

## 4. آلية البلوكشين

### هيكل الكتلة
```json
{
  "index":          3,
  "timestamp":      "2026-07-05T10:30:00.000Z",
  "encrypted_vote": "a3f5...hex...d9e0",
  "previous_hash":  "7b2c...64chars...f1a2",
  "current_hash":   "e91d...64chars...4f8a",
  "nonce":          0
}
```

### حساب SHA-256
```python
block_data = {
    "index":          self.index,
    "timestamp":      self.timestamp.isoformat(),
    "encrypted_vote": self.encrypted_vote,
    "previous_hash":  self.previous_hash,
    "nonce":          self.nonce
}
raw  = json.dumps(block_data, sort_keys=True)
hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
```

### سلسلة الربط
```
Genesis Block          Block 1               Block 2
┌─────────────┐        ┌────────────┐        ┌────────────┐
│ prev: 000…  │        │ prev: a3f5…│        │ prev: 7b2c…│
│ hash: a3f5… │──────► │ hash: 7b2c…│──────► │ hash: e91d…│
│ vote: GENESIS│        │ vote: enc1 │        │ vote: enc2 │
└─────────────┘        └────────────┘        └────────────┘
```

### كشف التلاعب
```python
def verify_integrity(self):
    for i in range(1, len(self.chain)):
        current  = self.chain[i]
        previous = self.chain[i - 1]
        # فحص 1: هل الـ hash صحيح؟
        if current.hash != current.calculate_hash():
            return False, f"Block {i}: hash مُزوَّر"
        # فحص 2: هل الرابط سليم؟
        if current.previous_hash != previous.hash:
            return False, f"Block {i}: السلسلة مكسورة"
    return True, "السلسلة سليمة ✓"
```

---

## 5. تشفير RSA-4096

```
┌──────────────────────────────────────────────────────────┐
│                    تشفير الصوت                            │
│                                                           │
│  vote_data = {"candidate_id": 3, "nfc_uid": "04A1..."}   │
│       │                                                   │
│       ▼                                                   │
│  json.dumps(vote_data) → UTF-8 bytes                      │
│       │                                                   │
│       ▼                                                   │
│  RSA-4096-OAEP (SHA-256 + MGF1)                          │
│  + المفتاح العام (public_key.pem)                         │
│       │                                                   │
│       ▼                                                   │
│  encrypted_bytes → .hex() → "a3f5d8b2..."                │
│       │                                                   │
│       ▼                                                   │
│  حفظ في جدول blockchain.encrypted_vote                    │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│              فك تشفير الأصوات (بعد الانتخابات)            │
│                                                           │
│  POST /api/decrypt-votes                                  │
│  { "private_key_password": "..." }                        │
│       │                                                   │
│       ▼                                                   │
│  تحميل private_key_encrypted.pem + كلمة المرور            │
│       │                                                   │
│       ▼                                                   │
│  RSA-4096-OAEP decrypt → JSON bytes                       │
│       │                                                   │
│       ▼                                                   │
│  {"candidate_id": 3, "nfc_uid": "...", "voted_at": "..."} │
│       │                                                   │
│       ▼                                                   │
│  تجميع + حساب النسب + عرض في Dashboard                    │
└──────────────────────────────────────────────────────────┘
```

---

## 6. نقاط النهاية REST

| Method | Endpoint | الحماية | الوصف |
|--------|----------|---------|-------|
| GET | `/api/health` | — | صحة النظام |
| POST | `/api/admin/login` | — | تسجيل دخول |
| POST | `/api/admin/logout` | JWT | تسجيل خروج |
| GET | `/api/voter-status/:uid` | — | أهلية الناخب |
| GET | `/api/candidates` | — | قائمة المرشحين |
| POST | `/api/vote` | — | تسجيل صوت |
| GET | `/api/verify-chain` | — | سلامة السلسلة |
| GET | `/api/blockchain/status` | — | حالة السلسلة |
| GET | `/api/stats` | — | إحصائيات حية |
| POST | `/api/decrypt-votes` | JWT(ADMIN) | فك التشفير |

---

## 7. Clean Architecture — Flutter

```
lib/
├── core/          ← لا يعتمد على أي طبقة أخرى
│   ├── constants/ ← ألوان، نصوص، ثيم
│   └── utils/     ← API client
│
├── domain/        ← منطق الأعمال الخالص
│   ├── entities/  ← Voter, Candidate, VoteReceipt
│   ├── repositories/ ← VotingRepository (abstract)
│   └── usecases/  ← CheckVoter, GetCandidates, CastVote
│
├── data/          ← تنفيذ الاتصال الخارجي
│   ├── models/    ← CandidateModel, VoterModel, VoteResultModel
│   ├── datasources/ ← RemoteDataSource (HTTP)
│   └── repositories/ ← VotingRepositoryImpl
│
└── presentation/  ← Flutter UI
    ├── providers/ ← VotingProvider (state management)
    ├── screens/   ← 10 شاشات
    └── widgets/   ← مكونات قابلة للإعادة
```

**قاعدة الاعتماد:** كل طبقة تعتمد فقط على الطبقة الداخلية.
- `presentation` ← `domain` ← لا شيء
- `data` ← `domain`
- `presentation` تستخدم `data` عبر Provider

---

## 8. إجراءات الأمان الإضافية

### منع التصويت المزدوج
```sql
-- في جدول voters
has_voted BOOLEAN DEFAULT FALSE

-- عند التصويت (atomic update)
UPDATE voters SET has_voted = TRUE, voted_at = NOW()
WHERE nfc_uid = $1 AND has_voted = FALSE
-- إذا أثّر على 0 صفوف → رُفض (race condition protection)
```

### سجل المراجعة (Audit Trail)
كل إجراء مُسجَّل في `audit_log`:
```
VOTE_CAST      — صوت ناجح
VOTE_ATTEMPT   — محاولة تصويت (نجاح/فشل)
VOTER_CHECK    — فحص أهلية
ADMIN_LOGIN    — دخول مشرف
ADMIN_LOGOUT   — خروج مشرف
DECRYPT_RESULTS — فك التشفير
CHAIN_VERIFY   — التحقق من السلسلة
```

### حماية الجلسة
- Token: `secrets.token_hex(64)` = 128 حرف hex عشوائي
- مدة الصلاحية: 8 ساعات (قابل للتعديل)
- الإلغاء: `is_revoked = TRUE` عند الخروج
- bcrypt rounds=12 لتشفير كلمات المرور

---

## 9. الحماية من هجمات الإعادة (Replay Attacks)

كل صوت مشفر يحتوي `voted_at` timestamp:
```python
vote_data["voted_at"] = datetime.now(timezone.utc).isoformat()
```

حتى لو استُنسخ الـ ciphertext، لن يؤثر لأن:
1. `has_voted = TRUE` يمنع تكرار التصويت بنفس NFC UID
2. كل vote_hash فريد في السلسلة (UNIQUE constraint)

---

## 10. متطلبات التشغيل

| المكون | الإصدار | الملاحظة |
|--------|---------|---------|
| Python | 3.11+ | Backend |
| PostgreSQL | 15+ | قاعدة البيانات |
| Flutter | 3.22+ | Kiosk App |
| Node.js | 20+ | Dashboard |
| OpenSSL | 3.0+ | توليد المفاتيح |

### الموارد المطلوبة
- RAM: 2GB كحد أدنى (4GB مُستحسن)
- Storage: 10GB (للبلوكشين + السجلات)
- Network: LAN محلية (لا يلزم إنترنت)
- CPU: x86_64 أو ARM64

---

## 11. إجراء يوم الانتخابات

```
قبل الانتخابات:
  1. python utils/key_generator.py --generate --password "كلمة_مرور_سرية"
  2. psql ... -f schema.sql && seed_data.sql
  3. python run.py  (تشغيل الخادم)
  4. flutter run    (تشغيل الكيوسك)
  5. npm start      (تشغيل Dashboard)

خلال التصويت:
  • المراقب يتابع الإحصائيات الحية من Dashboard
  • كل صوت يظهر فوراً عبر Socket.IO
  • زر "تحقق من السلسلة" لفحص النزاهة

بعد إغلاق باب التصويت:
  1. Dashboard → صفحة النتائج
  2. إدخال كلمة مرور المفتاح الخاص
  3. POST /api/decrypt-votes
  4. عرض النتائج + Pie Chart
```
