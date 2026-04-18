from .connection import get_supabase
import logging

logger = logging.getLogger(__name__)

class QueryExecutionError(Exception):
    pass

def execute_query(sql: str) -> dict:
    try:
        supabase = get_supabase()
        response = supabase.rpc('execute_sql', {'query_text': sql}).execute()
        rows_data = response.data or []

        if not rows_data:
            return {"columns": [], "rows": [], "count": 0}

        columns = list(rows_data[0].keys())
        rows = [
            [str(row[col]) if row[col] is not None and not isinstance(row[col], (int, float, bool)) else row[col]
             for col in columns]
            for row in rows_data
        ]
        return {"columns": columns, "rows": rows, "count": len(rows)}
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        raise QueryExecutionError(str(e))
