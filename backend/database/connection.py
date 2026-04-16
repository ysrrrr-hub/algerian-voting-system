"""
backend/database/connection.py
Database Connection Pool Manager
إدارة اتصالات PostgreSQL عبر Connection Pool
"""

import os
from dotenv import load_dotenv
import psycopg
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

load_dotenv()


class DatabaseManager:
    """
    Singleton Connection Pool Manager.
    يضمن فتح عدد محدود من الاتصالات وإعادة استخدامها.
    min_size=2: اتصالان جاهزان دائماً
    max_size=10: لا يتجاوز 10 اتصالات متزامنة
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
            conn_info = (
                f"host={os.getenv('DB_HOST', 'localhost')} "
                f"port={int(os.getenv('DB_PORT', 5432))} "
                f"dbname={os.getenv('DB_NAME', 'voting_system')} "
                f"user={os.getenv('DB_USER', 'voting_admin')} "
                f"password={os.getenv('DB_PASSWORD', '')} "
                f"client_encoding=UTF8"
            )
            self._pool = ConnectionPool(
                conn_info,
                min_size=2,
                max_size=10,
                kwargs={"row_factory": dict_row}
            )
            print("✅ Database connection pool initialized successfully")

    def get_connection(self) -> psycopg.Connection:
        """الحصول على اتصال من الـ Pool. يُستدعى في بداية كل طلب HTTP."""
        if self._pool is None:
            self.initialize()
        conn = self._pool.getconn()
        return conn

    def return_connection(self, conn: psycopg.Connection) -> None:
        """إعادة الاتصال للـ Pool بعد انتهاء الطلب."""
        if self._pool and conn and not conn.closed:
            # التراجع عن أي معاملات غير مكتملة قبل الإعادة
            conn.rollback()
            self._pool.putconn(conn)

    def close_all(self) -> None:
        """إغلاق جميع الاتصالات عند إيقاف التطبيق."""
        if self._pool:
            self._pool.close()
            self._pool = None
            print("✅ All database connections closed")

    @property
    def is_initialized(self) -> bool:
        return self._pool is not None


# Instance وحيدة يستخدمها التطبيق بالكامل
db_manager = DatabaseManager()
