from aiogram import Router, F
from aiogram.types import Message
from llm_parser import text_to_sql
from database import execute_sql

router = Router()

@router.message(F.text)
async def handle_message(message: Message):
    user_text = message.text.strip()
    if not user_text:
        return

    sql = await text_to_sql(user_text)
    result = await execute_sql(sql)

    await message.answer(str(result))