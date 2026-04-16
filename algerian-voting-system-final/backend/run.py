"""
backend/run.py
نقطة تشغيل الخادم

الاستخدام:
    cd backend
    python -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    python run.py
"""

import sys
import os

# السماح باستيراد الوحدات من المجلد الحالي
sys.path.insert(0, os.path.dirname(__file__))

from core.config import Config
from database.connection import db_manager
from api.routes import app
from api.socket_events import socketio


def main() -> None:
    print("=" * 62)
    print("  🗳️  نظام التصويت الإلكتروني الجزائري  —  2026")
    print("  Système de Vote Électronique Algérien")
    print("=" * 62)

    # 1. تهيئة Connection Pool
    db_manager.initialize()
    print(f"  🗄️  Database   : {Config.DB_NAME}@{Config.DB_HOST}:{Config.DB_PORT}")
    print(f"  🔑  Public key : {Config.PUBLIC_KEY_PATH}")
    print(f"  🗳️  Voting open: {Config.VOTING_OPEN}")
    print()

    # 2. ربط Socket.IO بـ Flask
    socketio.init_app(app, cors_allowed_origins="*")

    # 3. تشغيل الخادم
    print(f"  🚀  API      → http://0.0.0.0:{Config.API_PORT}")
    print(f"  📡  Health   → http://localhost:{Config.API_PORT}/api/health")
    print(f"  🔌  Socket   → ws://localhost:{Config.API_PORT}\n")

    socketio.run(
        app,
        host="0.0.0.0",
        port=Config.API_PORT,
        debug=Config.FLASK_DEBUG,
        use_reloader=False,
        log_output=Config.FLASK_DEBUG,
    )


if __name__ == "__main__":
    main()
