# Deployment Guide

## Domain: evotingdz.live
## Server: 209.38.44.237 (DigitalOcean Amsterdam)

## Services (systemd)
- `voting-backend.service` — Flask on :5000
- `voting-dashboard.service` — React on :3000
- `nginx.service` — Reverse proxy :80/:443

## SSL (Let's Encrypt)
- Auto-renewal via `certbot.timer`
- Manual renewal: `certbot renew`
- Test renewal: `certbot renew --dry-run`
- Certificate location: `/etc/letsencrypt/live/evotingdz.live/`

## URLs
- Public: https://evotingdz.live
- API: https://evotingdz.live/api/*
- Admin login: https://evotingdz.live (user: admin)

## Kiosk App — Dual Mode Support

The Flutter kiosk app supports two input modes:

### NFC Mode (Production)
- Default mode on devices with NFC hardware
- Voter taps NFC card on phone back
- Automatic card UID reading
- For: production deployment in voting centers

### Demo Mode (Testing/Presentation)
- Triggered by **3 taps on the green logo** (within 2 seconds)
- Opens dialog for manual UID entry
- Quick select buttons for 3 test voters
- For: development, testing, jury presentation

### Build APK
```bash
cd kiosk_app
flutter clean
flutter pub get
flutter build apk --release --split-per-abi
```

### Test Voter UIDs

| UID | Voter | Status |
|-----|-------|--------|
| 04A1B2C3D4E5F6 | Ahmed Ben Ali | Eligible |
| 04B2C3D4E5F6A1 | Fatima Bouaziz | Eligible |
| 04C3D4E5F6A1B2 | Mohamed Kasmi | Eligible |

### Configuration
API endpoint in `lib/core/utils/api_client.dart`:
- Base URL: https://evotingdz.live
- API prefix: /api
