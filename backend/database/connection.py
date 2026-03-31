# Vaani AI Banking Intelligence — Database Pool

import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from config import settings
import logging

logger = logging.getLogger(__name__)

class DatabasePool:
    def __init__(self):
        self._pool = None
        try:
            self._pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=2,
                maxconn=10,
                host=settings.supabase_db_host,
                port=settings.supabase_db_port,
                dbname=settings.supabase_db_name,
                user=settings.supabase_db_user,
                password=settings.supabase_db_password
            )
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Error initializing database pool: {e}")

    @contextmanager
    def get_connection(self):
        conn = self._pool.getconn()
        try:
            yield conn
        finally:
            self._pool.putconn(conn)

    def test_connection(self) -> bool:
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

# Singleton
db_pool = DatabasePool()
