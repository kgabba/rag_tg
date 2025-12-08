import os
import io
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_API_URL = os.getenv("API_BASE_URL")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# состояния больше не нужны — поведение автоматически определяется по типу сообщения

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Добро пожаловать!\n\n"
        "Отправь PDF/DOCX — и я добавлю его в базу 📄\n\n"
        "Или просто напиши вопрос по загруженным данным — и я отвечу 🙂"
    )

@dp.message(F.document)
async def handle_file(message: Message):
    doc = message.document

    # размер в байтах с стороны Telegram
    if doc.file_size and doc.file_size > 4 * 1024 * 1024:
        await message.answer("Файл больше 4 МБ, пришли что-нибудь поменьше 👇")
        return

    # проверяем расширение
    filename = doc.file_name or ""
    lower_name = filename.lower()
    if not (lower_name.endswith(".pdf") or lower_name.endswith(".docx")):
        await message.answer("Поддерживаются только PDF и DOCX.")
        return

    # качаем файл в память
    buf = io.BytesIO()
    await bot.download(doc, destination=buf)
    buf.seek(0)

    # шлём в FastAPI /llm/embed_file
    form = aiohttp.FormData()
    form.add_field(
        "file",
        buf,
        filename=filename,
        content_type=doc.mime_type or "application/octet-stream",
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE_API_URL}/llm/embed_file",
                data=form,
            ) as resp:
                data = await resp.json()
                if resp.status != 200:
                    await message.answer(f"Ошибка API: {data.get('detail', resp.status)}")
                    return
    except Exception as e:
        await message.answer(f"Ошибка при обращении к API: {e}")
        return

    chunks_count = data.get("chunks_added_counts", 0)
    await message.answer(f"Файл загружен, добавлено чанков: {chunks_count}\nТеперь можете задавать свой вопрос 🙂")

@dp.message()
async def handle_question(message: Message):
    # игнорируем команды типа /something (кроме /start handled separately)
    if not message.text or message.text.startswith("/"):
        return

    question = message.text.strip()
    if not question:
        await message.answer("Вопрос пустой, попробуй ещё раз 👇")
        return

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
