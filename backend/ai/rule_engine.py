import re
import logging

logger = logging.getLogger(__name__)

MONTH_MAP = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12,
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
}


class RuleBasedAnalyzer:
    TABLE = "user_uploaded_data"

    def _get_columns(self) -> list:
        try:
            from database.connection import get_supabase
            sb = get_supabase()
            resp = sb.rpc('execute_sql', {
                'query_text': (
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'user_uploaded_data' ORDER BY ordinal_position"
                )
            }).execute()
            return [row['column_name'].lower() for row in (resp.data or [])]
        except Exception as e:
            logger.error(f"Failed to fetch columns: {e}")
            return []

    def _find(self, cols, *keywords):
        for col in cols:
            if any(k in col for k in keywords):
                return col
        return None

    def _safe_num(self, col: str) -> str:
        """Cast a TEXT column to numeric, ignoring currency symbols and commas."""
        return f"NULLIF(REGEXP_REPLACE(\"{col}\", '[^0-9.-]', '', 'g'), '')::numeric"

    def _date_col(self, cols):
        return self._find(cols, 'date', 'time', 'created_at', 'timestamp', 'day')

    def _withdrawal_col(self, cols):
        return self._find(cols, 'withdrawal', 'debit', ' dr', 'expense', 'outflow')

    def _deposit_col(self, cols):
        return self._find(cols, 'deposit', 'credit', ' cr', 'income', 'inflow')

    def _balance_col(self, cols):
        return self._find(cols, 'balance', 'closing', 'available', 'vault')

    def _amount_col(self, cols):
        return self._find(cols, 'amount', 'value', 'price', 'amt')

    def _desc_col(self, cols):
        return self._find(cols, 'particular', 'description', 'narration', 'detail', 'remark', 'name', 'payee', 'merchant')

    def _type_col(self, cols):
        return self._find(cols, 'type', 'txn_type', 'transaction_type', 'cr_dr', 'category', 'mode')

    def _date_filter(self, q, cols):
        dc = self._date_col(cols)
        if not dc:
            return ""
        for name, num in MONTH_MAP.items():
            if name in q:
                return f" AND EXTRACT(MONTH FROM \"{dc}\"::date) = {num}"
        if 'today' in q:
            return f" AND \"{dc}\"::date = CURRENT_DATE"
        if 'yesterday' in q:
            return f" AND \"{dc}\"::date = CURRENT_DATE - INTERVAL '1 day'"
        if 'last 30 days' in q or '30 days' in q:
            return f" AND \"{dc}\"::date >= CURRENT_DATE - INTERVAL '30 days'"
        if 'this week' in q or ('week' in q and 'last' not in q and 'vs' not in q and 'compare' not in q):
            return f" AND \"{dc}\"::date >= CURRENT_DATE - INTERVAL '7 days'"
        if 'last month' in q:
            return f" AND EXTRACT(MONTH FROM \"{dc}\"::date) = EXTRACT(MONTH FROM CURRENT_DATE - INTERVAL '1 month')"
        if 'this month' in q:
            return f" AND EXTRACT(MONTH FROM \"{dc}\"::date) = EXTRACT(MONTH FROM CURRENT_DATE)"
        return ""

    def _amount_filter(self, q, col):
        if not col:
            return ""
        m = re.search(r'(?:greater than|above|more than|over|exceed[s]?)\s*[₹rRsS.]*\s*(\d[\d,]*)', q)
        if m:
            return f" AND NULLIF(REGEXP_REPLACE(\"{col}\", '[^0-9.-]', '', 'g'), '')::numeric > {m.group(1).replace(',', '')}"
        m = re.search(r'(?:less than|below|under|within)\s*[₹rRsS.]*\s*(\d[\d,]*)', q)
        if m:
            return f" AND NULLIF(REGEXP_REPLACE(\"{col}\", '[^0-9.-]', '', 'g'), '')::numeric < {m.group(1).replace(',', '')}"
        return ""

    def generate_sql(self, query: str) -> str:
        q = query.lower().strip()
        T = self.TABLE
        cols = self._get_columns()

        dc       = self._date_col(cols)
        desc_col = self._desc_col(cols)
        type_col = self._type_col(cols)
        w_col    = self._withdrawal_col(cols)
        d_col    = self._deposit_col(cols)
        bal_col  = self._balance_col(cols)
        amt_col  = self._amount_col(cols) or w_col or d_col

        df = self._date_filter(q, cols)

        # Q3 — column listing
        if re.search(r'\b(what|which)\b.*\bcolumn', q) or re.search(r'\bcolumns?\b.*(present|available|exist|in\s+my)', q):
            return (
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'user_uploaded_data' ORDER BY ordinal_position"
            )

        # Q23 — duplicates
        if 'duplicate' in q:
            if cols:
                cs = ', '.join([f'"{c}"' for c in cols])
                return f'SELECT {cs}, COUNT(*) as duplicate_count FROM {T} GROUP BY {cs} HAVING COUNT(*) > 1'
            return f"SELECT * FROM {T} LIMIT 100"

        # Q25 — ratio deposits to withdrawals
        if 'ratio' in q and d_col and w_col:
            nd, nw = self._safe_num(d_col), self._safe_num(w_col)
            return (
                f'SELECT ROUND(SUM({nd}), 2) as total_deposits, '
                f'ROUND(SUM({nw}), 2) as total_withdrawals, '
                f'ROUND(SUM({nd}) / NULLIF(SUM({nw}), 0), 4) as ratio '
                f'FROM {T}'
            )

        # Q20 — compare this week vs last week
        if ('compare' in q or ' vs ' in q) and 'week' in q and dc:
            col = w_col or amt_col
            if col:
                nc = self._safe_num(col)
                return (
                    f'SELECT '
                    f'ROUND(SUM(CASE WHEN "{dc}"::date >= CURRENT_DATE - INTERVAL \'7 days\' THEN {nc} ELSE 0 END), 2) as this_week, '
                    f'ROUND(SUM(CASE WHEN "{dc}"::date >= CURRENT_DATE - INTERVAL \'14 days\' AND "{dc}"::date < CURRENT_DATE - INTERVAL \'7 days\' THEN {nc} ELSE 0 END), 2) as last_week '
                    f'FROM {T}'
                )

        # Q21/Q22 — group by
        if re.search(r'\b(group\s+by|group\s+the|for\s+each|by\s+category|by\s+type|per\s+type|per\s+category)\b', q):
            gc = type_col or desc_col
            if gc:
                sc = d_col or w_col or amt_col
                if sc:
                    return f'SELECT "{gc}", COUNT(*) as count, ROUND(SUM({self._safe_num(sc)}), 2) as total FROM {T} GROUP BY "{gc}" ORDER BY total DESC'
                return f'SELECT "{gc}", COUNT(*) as count FROM {T} GROUP BY "{gc}" ORDER BY count DESC'

        # Q21 — highest entries by category/particulars
        if re.search(r'\b(highest|most)\b.*(entries|count|records|number)', q):
            gc = type_col or desc_col
            if gc:
                return f'SELECT "{gc}", COUNT(*) as count FROM {T} GROUP BY "{gc}" ORDER BY count DESC LIMIT 10'

        # Q24 — balance trend over time
        if re.search(r'\b(trend|over\s+time)\b', q) and bal_col:
            order = f'ORDER BY "{dc}"' if dc else ""
            select = f'"{dc}", ' if dc else ""
            return f'SELECT {select}"{bal_col}" FROM {T} {order}'

        # Q13 — count
        if re.search(r'\b(how many|count|total\s+rows?|number\s+of\s+rows?)\b', q):
            return f"SELECT COUNT(*) as total_rows FROM {T} WHERE 1=1{df}"

        # Q15 — maximum / highest balance
        if re.search(r'\b(max|maximum|highest|largest)\b', q):
            col = bal_col or d_col or w_col or amt_col
            if col:
                return f'SELECT MAX({self._safe_num(col)}) as maximum_value FROM {T} WHERE 1=1{df}'

        # Minimum
        if re.search(r'\b(min|minimum|lowest|smallest)\b', q):
            col = bal_col or d_col or w_col or amt_col
            if col:
                return f'SELECT MIN({self._safe_num(col)}) as minimum_value FROM {T} WHERE 1=1{df}'

        # Q14 — average
        if re.search(r'\b(average|avg|mean)\b', q):
            col = amt_col or d_col or w_col or bal_col
            if col:
                return f'SELECT ROUND(AVG({self._safe_num(col)}), 2) as average_value FROM {T} WHERE 1=1{df}'

        # Q11 — total deposits
        if re.search(r'\b(total|sum)\b', q) and re.search(r'\b(deposit|credit|income|inflow)\b', q):
            if d_col:
                return f'SELECT ROUND(SUM({self._safe_num(d_col)}), 2) as total_deposits FROM {T} WHERE 1=1{df}'

        # Q12 — total withdrawals / expenditure
        if re.search(r'\b(total|sum|expenditure|expense|spending)\b', q) and re.search(r'\b(withdrawal|debit|expense|spend|outflow)\b', q):
            if w_col:
                return f'SELECT ROUND(SUM({self._safe_num(w_col)}), 2) as total_withdrawals FROM {T} WHERE 1=1{df}'

        # Generic sum
        if re.search(r'\b(total|sum|aggregate)\b', q):
            col = amt_col or d_col or w_col or bal_col
            if col:
                return f'SELECT ROUND(SUM({self._safe_num(col)}), 2) as total_value FROM {T} WHERE 1=1{df}'

        # Q7/Q9 — amount threshold filter
        if re.search(r'(?:greater than|above|more than|less than|below|over|under)\s*[₹rRsS.]*\s*\d', q):
            if re.search(r'\b(withdrawal|debit|expense|spend)\b', q):
                col = w_col or amt_col
            elif re.search(r'\b(deposit|credit|income)\b', q):
                col = d_col or amt_col
            else:
                col = amt_col or d_col or w_col
            if col:
                af = self._amount_filter(q, col)
                return f'SELECT * FROM {T} WHERE 1=1{af}{df} LIMIT 200'

        # Q10 — credit/debit type filter
        if re.search(r'\b(only\s+)?(credit|cr)\b', q) and type_col:
            return f"SELECT * FROM {T} WHERE LOWER(\"{type_col}\") ILIKE '%credit%'{df} LIMIT 200"
        if re.search(r'\b(only\s+)?(debit|dr)\b', q) and type_col:
            return f"SELECT * FROM {T} WHERE LOWER(\"{type_col}\") ILIKE '%debit%'{df} LIMIT 200"

        # Q8 — multi-keyword OR search (quoted terms)
        quoted = re.findall(r"['\"]([^'\"]{2,})['\"]", query)
        if len(quoted) >= 2 and desc_col:
            cond = ' OR '.join([f'"{desc_col}" ILIKE \'%{t.replace(chr(39), chr(39)*2)}%\'' for t in quoted])
            return f"SELECT * FROM {T} WHERE ({cond}){df} LIMIT 200"

        # Q6 — single-term search
        sm = re.search(r"\b(?:find|search|look\s+for|containing)\b.*?['\"]([^'\"]+)['\"]", query)
        if not sm:
            sm = re.search(r"\bname\s+is\s+['\"]?([a-zA-Z][a-zA-Z0-9 ]+)['\"]?", query)
        if sm and desc_col:
            term = sm.group(1).strip().replace("'", "''")
            return f"SELECT * FROM {T} WHERE \"{desc_col}\" ILIKE '%{term}%'{df} LIMIT 200"

        # Q5 — summary / overview
        if re.search(r'\b(summary|overview|quick|describe|statistics|stats)\b', q):
            parts = ["COUNT(*) as total_rows"]
            if d_col:
                parts.append(f'ROUND(SUM({self._safe_num(d_col)}), 2) as total_deposits')
            if w_col:
                parts.append(f'ROUND(SUM({self._safe_num(w_col)}), 2) as total_withdrawals')
            if bal_col:
                parts.append(f'MAX({self._safe_num(bal_col)}) as max_balance')
                parts.append(f'MIN({self._safe_num(bal_col)}) as min_balance')
            return f"SELECT {', '.join(parts)} FROM {T}"

        # Q4 — show specific named columns
        target_cols = [c for c in cols if c in q and 'unnamed' not in c]
        if target_cols and re.search(r'\b(show|list|get|display|view|only)\b', q):
            cs = ', '.join([f'"{c}"' for c in target_cols])
            return f'SELECT {cs} FROM {T} WHERE 1=1{df} LIMIT 100'

        # Q1 — show all
        if re.search(r'\b(all|everything|complete|full|entire)\b', q):
            return f"SELECT * FROM {T} WHERE 1=1{df}"

        # Q2 — first N rows
        lm = re.search(r'\b(?:first|last|top|show|list)\s+(\d+)\b', q)
        limit = lm.group(1) if lm else "100"
        return f"SELECT * FROM {T} WHERE 1=1{df} LIMIT {limit}"


rule_engine = RuleBasedAnalyzer()
