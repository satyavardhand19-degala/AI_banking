# Vaani AI Banking Intelligence — SQL Executor

from .connection import db_pool
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
            with conn.cursor() as cursor:
                # Set statement timeout (30 seconds)
                cursor.execute("SET statement_timeout = '30000'")
                
                # Execute the actual query
                cursor.execute(sql)
                
                # Fetch results if it's a SELECT query
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    # Convert Decimals and other types to JSON-serializable formats
                    formatted_rows = []
                    for row in rows:
                        formatted_rows.append([str(item) if hasattr(item, '__str__') and not isinstance(item, (int, float, str, bool, type(None))) else item for item in row])
                    
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
    except Exception as e:
        logger.error(f"SQL Execution Error: {e}")
        raise QueryExecutionError(str(e))
