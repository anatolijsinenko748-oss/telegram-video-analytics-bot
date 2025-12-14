from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from dotenv import load_dotenv
import os

load_dotenv()

DB_URL = f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_async_engine(DB_URL, echo=False)


async def execute_sql(sql: str) -> str:
    async with AsyncSession(engine) as session:
        try:
            sql = sql.strip()
            if sql.endswith(';'):
                sql = sql[:-1].strip()

            result = await session.execute(text(sql))

            if not result.returns_rows:
                await session.commit()
                return "0"

            # Получаем первую строку
            row = result.fetchone()
            if row is None:
                return "0"

            # Возвращаем первое значение как строку
            value = row[0]
            return str(value) if value is not None else "0"

        except Exception as e:
            print(f"SQL Error: {e}\nSQL: {sql}")
            return "0"