# Nginx Configuration

## Installation on server
```bash
sudo cp voting-system.conf /etc/nginx/sites-available/
sudo ln -sf /etc/nginx/sites-available/voting-system /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx
```

## Architecture
- Port 80 (Nginx) → forwards to:
  - `/`        → Dashboard on :3000
  - `/api/`    → Flask backend on :5000
  - `/socket.io/` → Flask WebSocket on :5000
