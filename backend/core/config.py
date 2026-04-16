"""
backend/core/config.py
Application Configuration — إعدادات التطبيق المركزية
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # === قاعدة البيانات ===
    DB_HOST     = os.getenv("DB_HOST", "localhost")
    DB_PORT     = int(os.getenv("DB_PORT", 5432))
    DB_NAME     = os.getenv("DB_NAME", "voting_system")
    DB_USER     = os.getenv("DB_USER", "voting_admin")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")

    # === الأمان ===
    SECRET_KEY       = os.getenv("SECRET_KEY", "change-me-in-production-use-256-bits")
    PUBLIC_KEY_PATH  = os.getenv("PUBLIC_KEY_PATH",  "../secure/public_key.pem")
    PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH", "../secure/private_key_encrypted.pem")

    # === الخادم ===
    API_PORT        = int(os.getenv("API_PORT", 5000))
    FLASK_DEBUG     = os.getenv("FLASK_DEBUG", "False") == "True"
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

    # === الجلسات ===
    SESSION_EXPIRY_HOURS = int(os.getenv("SESSION_EXPIRY_HOURS", 8))

    # === التصويت ===
    VOTING_OPEN  = os.getenv("VOTING_OPEN",  "True")  == "True"
    ELECTION_YEAR = os.getenv("ELECTION_YEAR", "2026")
