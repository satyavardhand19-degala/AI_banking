# Vaani AI Banking Intelligence — Database Pool

import sqlite3
try:
    import psycopg2
    from psycopg2 import pool
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
from contextlib import contextmanager
from config import settings
import logging

logger = logging.getLogger(__name__)

class DatabasePool:
    def __init__(self):
        self._pool = None
        if settings.use_local_db:
            logger.info(f"Using local SQLite database: {settings.sqlite_db_path}")
        else:
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
                logger.info("Supabase connection pool initialized")
            except Exception as e:
                logger.error(f"Error initializing Supabase pool: {e}")

    @contextmanager
    def get_connection(self):
        if settings.use_local_db:
            # SQLite connection
            conn = sqlite3.connect(settings.sqlite_db_path)
            # Make it behave like psycopg2 (row factory)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()
        else:
            # Postgres connection
            conn = self._pool.getconn()
            try:
                yield conn
            finally:
                self._pool.putconn(conn)

    def test_connection(self) -> bool:
        try:
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

# Singleton
db_pool = DatabasePool()
