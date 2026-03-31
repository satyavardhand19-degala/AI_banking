# Vaani AI Banking Intelligence — SQL Validator

import re
from typing import Tuple, Optional

def validate_sql(sql: str) -> Tuple[bool, Optional[str]]:
    """
    Validates that the generated SQL is safe and read-only.
    """
    sql_upper = sql.upper().strip()
    
    # 1. Not empty
    if not sql_upper:
        return False, "empty_query"
        
    # 2. Must start with SELECT
    if not sql_upper.startswith("SELECT"):
        return False, "not_select"
        
    # 3. Blocklist for mutating operations
    blocklist = [
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", 
        "CREATE", "EXEC", "EXECUTE", "GRANT", "REVOKE", "XP_"
    ]
    for keyword in blocklist:
        # Use regex to find whole words only
        if re.search(r'\b' + keyword + r'\b', sql_upper):
            return False, f"forbidden_keyword:{keyword.lower()}"
            
    # 4. No semicolons except at the very end
    if ";" in sql[:-1]:
        return False, "mid_query_semicolon"
        
    # 5. Table allowlist
    allowlist = ["customers", "accounts", "transactions"]
    # Extract words after FROM or JOIN
    tables_found = re.findall(r'\b(?:FROM|JOIN)\s+([a-zA-Z0-9_]+)', sql_upper)
    for table in tables_found:
        if table.lower() not in allowlist:
            return False, f"disallowed_table:{table.lower()}"
            
    # 6. Max length
    if len(sql) > 2000:
        return False, "query_too_long"
        
    return True, None
