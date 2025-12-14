import os
import requests
from dotenv import load_dotenv
from prompts import DB_SCHEMA_PROMPT

load_dotenv()

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = os.getenv("OLLAMA_MODEL", "deepseek-coder:6.7b")


async def text_to_sql(user_query: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": DB_SCHEMA_PROMPT},
            {"role": "user", "content": user_query}
        ],
        "stream": False,
        "temperature": 0.0,
        "max_tokens": 500
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)

        if response.status_code != 200:
            return "SELECT 0"

        data = response.json()

        if "message" not in data or "content" not in data["message"]:
            return "SELECT 0"

        sql = data["message"]["content"].strip()

        # Очистка
        sql = sql.replace("```sql", "").replace("```", "").strip()
        if sql.endswith(";"):
            sql = sql[:-1].strip()

        if not sql.upper().startswith("SELECT"):
            return "SELECT 0"

        return sql if sql else "SELECT 0"

    except Exception as e:
        return "SELECT 0"