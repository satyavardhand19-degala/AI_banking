import re
import logging

logger = logging.getLogger(__name__)

class RuleBasedAnalyzer:
    """
    Purely rule-based engine to translate natural language queries into SQL for PostgreSQL.
    Targets 'user_uploaded_data' which contains data uploaded by the user.
    """

    def generate_sql(self, query: str) -> str:
        q = query.lower().strip()
        table_name = "user_uploaded_data"
        cols = []
        
        # Try to fetch columns from the uploaded data in PostgreSQL to build better queries
        try:
            from database.connection import db_pool
            with db_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    query_schema = "SELECT column_name FROM information_schema.columns WHERE table_name = %s"
                    cursor.execute(query_schema, (table_name,))
                    res = cursor.fetchall()
                    cols = [x[0].lower() for x in res]
        except Exception as e:
            logger.error(f"Failed to fetch {table_name} columns from PostgreSQL: {e}")

        # 1. Column Selection / Mention
        target_columns = [c for c in cols if c in q and "unnamed" not in c]
        if target_columns and re.search(r'\b(show|list|get|display|view)\b', q):
            context_cols = [c for c in ["date", "particulars", "description"] if c in cols and c not in target_columns]
            all_target = context_cols + target_columns
            date_filter = self._get_date_filter(q, cols)
            return f'SELECT {", ".join([f"{c}" for c in all_target])} FROM {table_name} WHERE 1=1{date_filter} LIMIT 100'

        # 2. Basic Count
        if re.search(r'\b(how many|count)\b', q):
            date_filter = self._get_date_filter(q, cols)
            return f"SELECT COUNT(*) as total_rows FROM {table_name} WHERE 1=1{date_filter}"

        # 3. Sum / Total
        if re.search(r'\b(total|sum|aggregate)\b', q):
            target_col = next((c for c in cols if any(k in c for k in ["amount", "value", "total", "balance", "price", "withdrawals", "deposits"])), None)
            date_filter = self._get_date_filter(q, cols)
            if target_col:
                return f"SELECT SUM({target_col}) as total_value FROM {table_name} WHERE 1=1{date_filter}"
            return f"SELECT * FROM {table_name} WHERE 1=1{date_filter} LIMIT 100"

        # 4. Filter by Name/String
        match = re.search(r'\b(?:find|show|search)\s+(?!the\b|a\b|my\b|me\b|of\b|today\b|this\b)([a-zA-Z0-9]+)\b', q)
        if match:
            search_term = match.group(1).strip()
            if search_term not in ['all', 'records', 'data', 'everything', 'rows', 'the', 'my', 'me', 'list', 'show', 'vault', 'today', 'week', 'month']:
                name_col = next((c for c in cols if any(k in c for k in ["name", "customer", "user", "client", "description", "particulars"]) and "unnamed" not in c), None)
                if name_col:
                    date_filter = self._get_date_filter(q, cols)
                    return f"SELECT * FROM {table_name} WHERE {name_col} ILIKE '%{search_term}%'{date_filter}"

        # 5. Limit / Last / All
        date_filter = self._get_date_filter(q, cols)
        if re.search(r'\b(all|everything|complete|full|entire)\b', q):
            return f"SELECT * FROM {table_name} WHERE 1=1{date_filter}"

        limit_match = re.search(r'\b(?:last|first|show)\s+(\d+)\b', q)
        limit = limit_match.group(1) if limit_match else "100" 
        
        return f"SELECT * FROM {table_name} WHERE 1=1{date_filter} LIMIT {limit}"

    def _get_date_filter(self, query: str, cols: list) -> str:
        """Helper to extract date filters from the query string for PostgreSQL."""
        date_col = next((c for c in cols if any(k in c for k in ["date", "time", "created_at", "timestamp"])), None)
        if not date_col:
            return ""

        if "today" in query:
            return f" AND {date_col}::date = CURRENT_DATE"
        elif "week" in query:
            return f" AND {date_col} >= CURRENT_DATE - INTERVAL '7 days'"
        elif "month" in query:
            return f" AND {date_col} >= CURRENT_DATE - INTERVAL '30 days'"
        return ""

# Singleton instance
rule_engine = RuleBasedAnalyzer()
