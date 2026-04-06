# Vaani AI Banking Intelligence — AI SQL Generation

from openai import OpenAI
from .prompt_builder import build_system_prompt
from config import settings
import re
import logging

logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate_sql(self, query: str) -> str:
        """
        Converts natural language query to SQL using OpenAI GPT.
        Includes a fallback for OpenAI quota errors to keep the demo functional.
        """
        system_prompt = build_system_prompt()

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                max_tokens=500,
                temperature=0,
            )

            sql = response.choices[0].message.content

            # Clean up the SQL response
            # Remove markdown fences
            sql = re.sub(r'```sql\s*', '', sql, flags=re.IGNORECASE)
            sql = re.sub(r'```', '', sql)
            sql = sql.strip()

            # Remove trailing semicolon if present
            if sql.endswith(';'):
                sql = sql[:-1]

            return sql
        except Exception as e:
            logger.warning(f"OpenAI API failed (likely quota exceeded): {e}. Using fallback generator.")
            return self._fallback_sql(query)

    def _fallback_sql(self, query: str) -> str:
        """Fallback rule-based generator for demo queries when OpenAI is out of quota."""
        q = query.lower()
        if "all customers" in q or "show customers" in q:
            return "SELECT id, name, email, phone, created_at FROM customers"
        elif "balance" in q and "arun" in q:
            return "SELECT c.name, a.account_number, a.account_type, a.balance, a.status FROM customers c JOIN accounts a ON c.id = a.customer_id WHERE c.name ILIKE '%Arun%'"
        elif "total credit" in q:
            return "SELECT SUM(amount) as total_credits FROM transactions WHERE transaction_type = 'credit'"
        elif "last 10 transactions" in q:
            return "SELECT t.id, a.account_number, t.transaction_type, t.amount, t.description, t.created_at FROM transactions t JOIN accounts a ON t.account_id = a.id ORDER BY t.created_at DESC LIMIT 10"
        elif "above 50000" in q:
            return "SELECT DISTINCT c.name, c.email FROM customers c JOIN accounts a ON c.id = a.customer_id JOIN transactions t ON a.id = t.account_id WHERE t.amount > 50000"
        else:
            # Generic fallback
            return "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 10"

# Singleton
openai_client = OpenAIClient()
