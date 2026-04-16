import sys
import os
from config import settings
import psycopg2

def init_db():
    print("Connecting to Supabase PostgreSQL...")
    try:
        conn = psycopg2.connect(
            host=settings.supabase_db_host,
            port=settings.supabase_db_port,
            dbname=settings.supabase_db_name,
            user=settings.supabase_db_user,
            password=settings.supabase_db_password
        )
        conn.autocommit = True
        cursor = conn.cursor()

        print("Executing schema.sql...")
        with open('../supabase/schema.sql', 'r') as f:
            cursor.execute(f.read())

        print("Executing rls_policies.sql...")
        with open('../supabase/rls_policies.sql', 'r') as f:
            cursor.execute(f.read())

        print("Executing seed.sql...")
        with open('../supabase/seed.sql', 'r') as f:
            cursor.execute(f.read())

        cursor.close()
        conn.close()
        print("SUCCESS: Database initialization complete.")
    except Exception as e:
        print(f"FAILURE: Could not initialize the database. Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_db()