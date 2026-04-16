"""
backend/database/connection.py
Database Connection Pool Manager
إدارة اتصالات PostgreSQL عبر Connection Pool
"""

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()


class DatabaseManager:
    """
    Singleton Connection Pool Manager.
    يضمن فتح عدد محدود من الاتصالات وإعادة استخدامها.
    minconn=2: اتصالان جاهزان دائماً
    maxconn=10: لا يتجاوز 10 اتصالات متزامنة
    """
    _instance = None
    _pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self) -> None:
        """تهيئة الـ Connection Pool عند بدء التطبيق."""
        if self._pool is None:
            self._pool = pool.ThreadedConnectionPool(
                minconn=2,
                maxconn=10,
                host=os.getenv('DB_HOST', 'localhost'),
                port=int(os.getenv('DB_PORT', 5432)),
                database=os.getenv('DB_NAME', 'voting_system'),
                user=os.getenv('DB_USER', 'voting_admin'),
                password=os.getenv('DB_PASSWORD', ''),
                cursor_factory=RealDictCursor,
                options="-c client_encoding=UTF8"
            )
            print("✅ Database connection pool initialized successfully")

    def get_connection(self) -> psycopg2.extensions.connection:
        """الحصول على اتصال من الـ Pool. يُستدعى في بداية كل طلب HTTP."""
        if self._pool is None:
            self.initialize()
        conn = self._pool.getconn()
        if conn.closed:
            # إذا كان الاتصال مغلقاً (timeout)، نطلب واحداً جديداً
            self._pool.putconn(conn)
            conn = self._pool.getconn()
        return conn

    def return_connection(self, conn: psycopg2.extensions.connection) -> None:
        """إعادة الاتصال للـ Pool بعد انتهاء الطلب."""
        if self._pool and conn and not conn.closed:
            # التراجع عن أي معاملات غير مكتملة قبل الإعادة
            conn.rollback()
            self._pool.putconn(conn)

    def close_all(self) -> None:
        """إغلاق جميع الاتصالات عند إيقاف التطبيق."""
        if self._pool:
            self._pool.closeall()
            self._pool = None
            print("✅ All database connections closed")

    @property
    def is_initialized(self) -> bool:
        return self._pool is not None


# Instance وحيدة يستخدمها التطبيق بالكامل
db_manager = DatabaseManager()
