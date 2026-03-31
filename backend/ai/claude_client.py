# Vaani AI Banking Intelligence — AI SQL Generation

import openai
from .prompt_builder import build_system_prompt
from config import settings
import re

class OpenAIClient:
    def __init__(self):
        openai.api_key = settings.openai_api_key

    def generate_sql(self, query: str) -> str:
        """
        Converts natural language query to SQL using OpenAI GPT.
        """
        system_prompt = build_system_prompt()

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Using GPT-3.5-turbo for cost efficiency
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            max_tokens=500,
            temperature=0,
        )

        sql = response['choices'][0]['message']['content']

        # Clean up the SQL response
        # Remove markdown fences
        sql = re.sub(r'```sql\s*', '', sql)
        sql = re.sub(r'```', '', sql)
        sql = sql.strip()

        # Remove trailing semicolon if present (validator handles this too, but good practice)
        if sql.endswith(';'):
            sql = sql[:-1]

        return sql

# Singleton
openai_client = OpenAIClient()
