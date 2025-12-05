import os
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_API_URL = os.getenv("API_BASE_URL")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Простейшее хранилище состояния: кто сейчас "вводит вопрос"
WAITING_QUESTION_USERS: set[int] = set()

ask_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🧠 Задать вопрос")]],
    resize_keyboard=True,
)


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Добро пожаловать! Этот бот-приложение разработал Камиль.\n\n"
        "Нажми кнопку ниже, чтобы задать вопрос.",
        reply_markup=ask_keyboard,
    )


@dp.message(F.text == "🧠 Задать вопрос")
async def ask_button(message: Message):
    WAITING_QUESTION_USERS.add(message.from_user.id)
    await message.answer("Напиши свой вопрос одним сообщением 👇")


@dp.message()
async def handle_question(message: Message):
    # Игнорируем команды типа /something
    if message.text.startswith("/"):
        return

    user_id = message.from_user.id

    if user_id not in WAITING_QUESTION_USERS:
        await message.answer("Сначала нажми кнопку «🧠 Задать вопрос» 🙂")
        return

    question = message.text.strip()
    WAITING_QUESTION_USERS.discard(user_id)

    if not question:
        await message.answer("Вопрос пустой, попробуй ещё раз.")
        return

    # Дёргаем твой RAG API
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE_API_URL}/llm/ask",
                json={"text": question},
            ) as resp:
                data = await resp.json()
    except Exception as e:
        await message.answer(f"Ошибка при обращении к API: {e}")
        return

    answer = data.get("answer", "Ошибка на сервере")
    await message.answer(answer)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
