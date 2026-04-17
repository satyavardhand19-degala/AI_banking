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

# SQLAlchemy Engine for Pandas to_sql operations
# NullPool disables connection pooling — required for serverless (Vercel) where
# each invocation is a fresh process and pooled connections go stale instantly.
encoded_password = urllib.parse.quote_plus(settings.supabase_db_password)
URI = f"postgresql://{settings.supabase_db_user}:{encoded_password}@{settings.supabase_db_host}:{settings.supabase_db_port}/{settings.supabase_db_name}?sslmode=require"
engine = create_engine(URI, poolclass=NullPool)

class DatabasePool:
    def __init__(self):
        self._pool = None
        try:
            # Simple connection for the pooler
            self._pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                host=settings.supabase_db_host,
                port=settings.supabase_db_port,
                dbname=settings.supabase_db_name,
                user=settings.supabase_db_user,
                password=settings.supabase_db_password,
                sslmode='require',
                connect_timeout=15
            )
            logger.info("Successfully connected to Supabase Connection Pooler")
        except Exception as e:
            logger.error(f"Database Pool Error: {e}")

    @contextmanager
    def get_connection(self):
        if not self._pool:
            raise Exception("Database connection pool not initialized (check your Supabase credentials)")
            
        conn = self._pool.getconn()
        try:
            # Postgres connection
            yield conn
        finally:
            self._pool.putconn(conn)

    def test_connection(self) -> bool:
        if not self._pool:
            return False
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
