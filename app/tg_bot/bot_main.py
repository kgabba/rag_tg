import os
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_API_URL = os.getenv("BASE_API_URL", "http://api:8000")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(commands=["start"])
async def cmd_start(message: Message):
  await message.answer("Привет! Напиши вопрос, я спрошу RAG-API 🙂")

@dp.message(commands=["ask"])
async def cmd_ask(message: Message):
  # всё, что после /ask — считаем вопросом
  question = message.text.removeprefix("/ask").strip()
  if not question:
    await message.answer("Напиши вопрос после /ask")
    return

  async with aiohttp.ClientSession() as session:
    async with session.post(
      f"{BASE_API_URL}/llm/ask",
      json={"text": question},
    ) as resp:
      data = await resp.json()

  answer = data.get("answer", "Ошибка на сервере")
  await message.answer(answer)

async def main():
  dp.include_router(dp)  # для aiogram v3, если ты роутеры вынесешь отдельно
  await dp.start_polling(bot)

if __name__ == "__main__":
  asyncio.run(main())