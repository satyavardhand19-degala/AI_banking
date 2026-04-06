# Vaani AI Banking Intelligence — SQL Executor

from .connection import db_pool
from config import settings
import logging

logger = logging.getLogger(__name__)

class QueryExecutionError(Exception):
    pass

def execute_query(sql: str) -> dict:
    """
    Executes a read-only SQL query and returns the results.
    """
    try:
        with db_pool.get_connection() as conn:
            # For SQLite, conn.cursor() doesn't support context manager in all versions
            cursor = conn.cursor()
            try:
                # Set statement timeout for PostgreSQL only
                if not settings.use_local_db:
                    cursor.execute("SET statement_timeout = '30000'")
                
                # Execute the actual query
                cursor.execute(sql)
                
                # Fetch results if it's a SELECT query
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    
                    # Convert results to JSON-serializable formats
                    formatted_rows = []
                    for row in rows:
                        # Row might be a tuple (psycopg2) or sqlite3.Row
                        # Convert to list
                        row_list = list(row)
                        # Format special types (like Decimals or datetime) to strings
                        formatted_rows.append([str(item) if hasattr(item, '__str__') and not isinstance(item, (int, float, str, bool, type(None))) else item for item in row_list])
                    
                    return {
                        "columns": columns,
                        "rows": formatted_rows,
                        "count": len(rows)
                    }
                else:
                    return {
                        "columns": [],
                        "rows": [],
                        "count": cursor.rowcount
                    }
            finally:
                cursor.close()
    except Exception as e:
        logger.error(f"SQL Execution Error: {e}")
        raise QueryExecutionError(str(e))
