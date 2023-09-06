import asyncio
import logging
import sys
import os

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.types import FSInputFile

import asyncio
from datetime import datetime, time
os.environ.setdefault("TZ", "Europe/Moscow")

# Настройка Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zavodik.settings")
import django
django.setup()
from api.models import Chat


# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    try:
        myChat =  await Chat.objects.acreate(chat_id=message.chat.id)
        await myChat.asave()
    except:
        await message.answer("Чел, ты...")
        await asyncio.sleep(1)
        await message.answer("Работаешь на заводе")
    else:
        await message.answer("Я тебя добавил в список пидорасов")
        await message.answer("Теперь каждое утро, равно, сука, в 8:00,\nЯ буду напоминать тебе кто ты и где твоё место")
        await asyncio.sleep(3)
        await message.answer("Инженер хуев")


@dp.message()
async def echo_handler(message: types.Message) -> None:
    await message.answer("Работать!!!")

async def send_morning(bot: Bot):
    photo = FSInputFile("img/zavod.jpg")
    target = time(0, 9, 0)
    isWas = False
    while True:
        now = datetime.now().time()
        if now >= target:
            if not isWas:
                isWas = True
                async for chat in Chat.objects.all():
                    await bot.send_photo(chat.chat_id, photo)
        else:
            isWas = False

        await asyncio.sleep(10)

async def main() -> None:
    # Настройки бота
    TOKEN = os.getenv("BOT_TOKEN")
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    await asyncio.gather(dp.start_polling(bot),
                         send_morning(bot))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
