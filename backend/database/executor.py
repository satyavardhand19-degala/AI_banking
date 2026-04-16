# Vaani AI Banking Intelligence — SQL Executor (PostgreSQL Only)

from .connection import db_pool
from config import settings
import logging

logger = logging.getLogger(__name__)

class QueryExecutionError(Exception):
    pass

def execute_query(sql: str) -> dict:
    """
    Executes a read-only SQL query against the PostgreSQL pool and returns results.
    """
    try:
        with db_pool.get_connection() as conn:
            cursor = conn.cursor()
            try:
                # Set statement timeout for PostgreSQL
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
                        # Row is a tuple (psycopg2)
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
        logger.error(f"PostgreSQL Execution Error: {e}")
        raise QueryExecutionError(str(e))
