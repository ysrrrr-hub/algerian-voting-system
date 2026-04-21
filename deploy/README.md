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
