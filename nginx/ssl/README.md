# 🔒 SSL Certificates

هذا المجلد يحتوي على شهادات SSL. **لا تُرفع للـ Git.**

## توليد شهادة ذاتية للتطوير

```bash
cd nginx/ssl

# شهادة ذاتية صالحة لمدة سنة
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem \
    -days 365 -nodes \
    -subj "/C=DZ/ST=Alger/L=Alger/O=ANIE/CN=voting.dz"
```

## للإنتاج: شهادة Let's Encrypt

```bash
# تثبيت certbot
apt-get install certbot

# توليد شهادة مجانية
certbot certonly --standalone \
    -d voting.domain.dz \
    --email admin@domain.dz \
    --agree-tos \
    --non-interactive

# نسخ الشهادات
cp /etc/letsencrypt/live/voting.domain.dz/fullchain.pem nginx/ssl/cert.pem
cp /etc/letsencrypt/live/voting.domain.dz/privkey.pem   nginx/ssl/key.pem
```

## الملفات المطلوبة

| الملف | الوصف |
|-------|-------|
| `cert.pem` | الشهادة العامة (+ chain) |
| `key.pem`  | المفتاح الخاص للشهادة |
