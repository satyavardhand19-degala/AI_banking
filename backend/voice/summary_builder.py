# Vaani AI Banking Intelligence — Result Summary Builder

import logging

logger = logging.getLogger(__name__)

def build_summary(query: str, columns: list, rows: list, count: int) -> str:
    """
    Generates a concise, speakable summary of the query results.
    """
    if count == 0:
        return "I couldn't find any results matching your request."

    # Identify if it's an aggregation result (e.g., SUM, COUNT)
    is_aggregation = any(col.lower() in ['sum', 'total', 'count', 'avg'] for col in columns)
    
    if is_aggregation and count == 1:
        val = rows[0][0]
        return f"The total result for your query is {val}."

    # Handle transaction lists
    if "amount" in [c.lower() for c in columns]:
        amounts = []
        for row in rows:
            try:
                # Find index of amount column
                idx = [c.lower() for c in columns].index("amount")
                amounts.append(float(row[idx]))
            except:
                continue
        
        if amounts:
            max_amt = max(amounts)
            return f"I found {count} transactions. The largest amount is ₹{max_amt:,.2f}."
        else:
            return f"I found {count} transactions matching your criteria."

    # Default summary
    return f"I found {count} records matching your query."
