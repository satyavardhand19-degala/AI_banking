# Vaani AI Banking Intelligence — Database Pool (PostgreSQL Only)

import psycopg2
from psycopg2 import pool
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
from config import settings
import logging
import urllib.parse

logger = logging.getLogger(__name__)

# SQLAlchemy Engine for Pandas to_sql — NullPool for serverless (no persistent pool)
encoded_password = urllib.parse.quote_plus(settings.supabase_db_password)
URI = f"postgresql://{settings.supabase_db_user}:{encoded_password}@{settings.supabase_db_host}:{settings.supabase_db_port}/{settings.supabase_db_name}?sslmode=require"
engine = create_engine(URI, poolclass=NullPool)


class DatabasePool:
    def __init__(self):
        self._pool = None
        # Pool is created lazily on first use — avoids blocking at import time
        # which would cause Vercel serverless to time out before handling any request.

    def _ensure_pool(self):
        if self._pool is not None:
            return
        self._pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=5,
            host=settings.supabase_db_host,
            port=settings.supabase_db_port,
            dbname=settings.supabase_db_name,
            user=settings.supabase_db_user,
            password=settings.supabase_db_password,
            sslmode='require',
            connect_timeout=8,
        )
        logger.info("Database pool created")

    @contextmanager
    def get_connection(self):
        self._ensure_pool()
        conn = self._pool.getconn()
        try:
            yield conn
        finally:
            self._pool.putconn(conn)

    def test_connection(self) -> bool:
        try:
            self._ensure_pool()
            with self.get_connection() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("SELECT 1")
                    return True
                finally:
                    cursor.close()
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False


# Singleton — pool is not created until first request
db_pool = DatabasePool()
