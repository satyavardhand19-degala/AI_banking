# Vaani AI — System Prompt Builder (Dynamic Schema - PostgreSQL)

from datetime import datetime
from config import settings
from database.connection import db_pool
import logging

logger = logging.getLogger(__name__)

def build_dynamic_prompt(user_query: str) -> str:
    """
    Constructs a system prompt for the AI model based on the ACTUAL columns in the user's data vault in PostgreSQL.
    """
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    current_date = now.strftime("%Y-%m-%d")
    
    table_name = "user_uploaded_data"
    cols_info = []
    
    # Fetch actual columns from PostgreSQL to inform the AI
    try:
        with db_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                # Query information_schema for column names and types
                query = """
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = %s
                    ORDER BY ordinal_position
                """
                cursor.execute(query, (table_name,))
                res = cursor.fetchall()
                # res[0] is name, res[1] is type
                cols_info = [f"{x[0]} ({x[1]})" for x in res]
    except Exception as e:
        logger.error(f"Failed to fetch {table_name} columns from PostgreSQL for prompt: {e}")

    cols_str = ", ".join(cols_info) if cols_info else "Unknown (assume general columns)"

    prompt = f"""You are 'Vaani', a specialized SQL expert.
Your task is to convert natural language queries into valid PostgreSQL SELECT statements.

DATABASE TABLE:
- {table_name}
COLUMNS:
[{cols_str}]

CURRENT DATE: {current_date}
CURRENT TIME: {current_time}

STRICT RULES:
1. Respond with ONLY one valid PostgreSQL SELECT statement.
2. DO NOT include markdown, explanations, or backticks.
3. TABLE NAME is ALWAYS '{table_name}'.
4. Use ILIKE '%term%' (case-insensitive) for string searches.
5. For "today", use {table_name}.date_column::date = CURRENT_DATE (adjust column name).
6. For "this week", use {table_name}.date_column >= CURRENT_DATE - INTERVAL '7 days'.
7. Return all relevant rows unless a limit is specified.
8. If the query asks for "total" or "sum", use SUM(column_name).
9. Map user terms to the columns provided above. If a column looks like 'particulars' or 'description', use it for search.

EXAMPLES:
User: show all data
SQL: SELECT * FROM {table_name}

User: count rows
SQL: SELECT COUNT(*) FROM {table_name}

User: total value
SQL: SELECT SUM(amount) FROM {table_name} (adjust column name based on schema)
"""
    return prompt
