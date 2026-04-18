import re
from typing import Tuple, Optional

def validate_sql(sql: str) -> Tuple[bool, Optional[str]]:
    sql_upper = sql.upper().strip()

    if not sql_upper:
        return False, "empty_query"

    if not sql_upper.startswith("SELECT"):
        return False, "not_select"

    blocklist = [
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE",
        "CREATE", "EXEC", "EXECUTE", "GRANT", "REVOKE", "XP_",
    ]
    for kw in blocklist:
        if re.search(r'\b' + kw + r'\b', sql_upper):
            return False, f"forbidden_keyword:{kw.lower()}"

    if ";" in sql[:-1]:
        return False, "mid_query_semicolon"

    allowlist = {"user_uploaded_data", "information_schema", "columns"}
    tables_found = re.findall(r'\b(?:FROM|JOIN)\s+([a-zA-Z0-9_]+)', sql_upper)
    for table in tables_found:
        if table.lower() not in allowlist:
            return False, f"disallowed_table:{table.lower()}"

    if len(sql) > 4000:
        return False, "query_too_long"

    return True, None
