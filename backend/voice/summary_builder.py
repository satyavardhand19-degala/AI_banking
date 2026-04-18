import logging

logger = logging.getLogger(__name__)

def _fmt(val) -> str:
    try:
        return f"₹{float(val):,.2f}"
    except (TypeError, ValueError):
        return str(val)

def build_summary(query: str, columns: list, rows: list, count: int) -> str:
    if count == 0:
        return "No results found matching your request."

    q = query.lower()
    cols_lower = [c.lower() for c in columns]

    # Column listing
    if 'column_name' in cols_lower:
        names = [str(r[0]) for r in rows]
        return f"Your data has {len(names)} columns: {', '.join(names)}."

    # Single-row aggregation results
    if count == 1 and len(rows[0]) <= 6:
        parts = []
        for col, val in zip(columns, rows[0]):
            c = col.lower()
            if val is None:
                continue
            if any(k in c for k in ['total', 'sum', 'deposit', 'withdrawal', 'value', 'balance', 'maximum', 'minimum', 'average']):
                parts.append(f"{col.replace('_', ' ').title()}: {_fmt(val)}")
            elif 'ratio' in c:
                parts.append(f"Ratio: {val}")
            elif 'row' in c or 'count' in c:
                parts.append(f"Total rows: {val}")
            elif 'week' in c:
                parts.append(f"{col.replace('_', ' ').title()}: {_fmt(val)}")
            else:
                parts.append(f"{col.replace('_', ' ').title()}: {val}")
        if parts:
            return '. '.join(parts) + '.'

    # Duplicate detection
    if 'duplicate_count' in cols_lower:
        return f"Found {count} duplicate record group(s) in your data."

    # Group by results
    if count > 1 and any(k in cols_lower for k in ['count', 'total']):
        top = rows[0]
        label_idx = 0
        count_idx = next((i for i, c in enumerate(cols_lower) if 'count' in c), None)
        total_idx = next((i for i, c in enumerate(cols_lower) if 'total' in c), None)

        if count_idx is not None:
            label = top[label_idx]
            top_count = top[count_idx]
            msg = f"Found {count} groups. Top category: '{label}' with {top_count} entries"
            if total_idx is not None:
                msg += f" totalling {_fmt(top[total_idx])}"
            return msg + "."

    # Trend / balance over time
    if any('balance' in c for c in cols_lower) and count > 1:
        try:
            vals = [float(r[-1]) for r in rows if r[-1] is not None]
            if vals:
                return (
                    f"Balance trend over {count} records: "
                    f"starts at {_fmt(vals[0])}, ends at {_fmt(vals[-1])}, "
                    f"peak {_fmt(max(vals))}, low {_fmt(min(vals))}."
                )
        except Exception:
            pass

    # Transaction list
    if count > 1:
        amt_idx = next(
            (i for i, c in enumerate(cols_lower) if any(k in c for k in ['amount', 'deposit', 'withdrawal', 'credit', 'debit', 'value'])),
            None
        )
        if amt_idx is not None:
            try:
                amounts = [float(r[amt_idx]) for r in rows if r[amt_idx] is not None]
                if amounts:
                    return (
                        f"Found {count} records. "
                        f"Largest: {_fmt(max(amounts))}, "
                        f"Total: {_fmt(sum(amounts))}."
                    )
            except Exception:
                pass

    return f"Found {count} records matching your query."
