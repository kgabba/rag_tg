import os
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_API_URL = os.getenv("API_BASE_URL")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет! Напиши /ask твой_вопрос – я спрошу RAG-API 🙂")


@dp.message(Command("ask"))
async def cmd_ask(message: Message):
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
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
