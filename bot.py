import asyncio
import logging
import sys
import os

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import FSInputFile
from aiogram.types import BotCommand
from aiogram.types import  BotCommandScopeDefault
from aiogram.filters import Filter

import redis.asyncio as redis

import asyncio
from datetime import datetime, time
from zoneinfo import ZoneInfo

# Настройка Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zavodik.settings")
import django
django.setup()
from api.models import Chat

class SlaveFilter(Filter):
    async def __call__(self, msg: Message) -> bool:
        try:
            chat = await Chat.objects.aget(chat_id=msg.chat.id)
        except Chat.DoesNotExist:
            return False
        return True

class NotSlaveFilter(Filter):
    async def __call__(self, msg: Message) -> bool:
        try:
            chat = await Chat.objects.aget(chat_id=msg.chat.id)
        except Chat.DoesNotExist:
            return True
        return False

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()

@dp.message(Command('start'))
async def command_start_handler(message: Message) -> None:
    try:
        myChat =  await Chat.objects.acreate(chat_id=message.chat.id)
        await myChat.asave()
    except:
        await message.answer("Чел, ты...")
        await asyncio.sleep(1)
        await message.answer("Работаешь на заводе")
    else:
        await message.answer("Я добавил тебя в список пидорасов")
        await asyncio.sleep(1)
        await message.answer("Теперь каждое утро, ровно, сука, в 8:00,\nЯ буду напоминать тебе кто ты и где твоё место")
        await asyncio.sleep(2)
        await message.answer("Инженер хуев")

@dp.message(Command('quit'), SlaveFilter())
async def command_quit_handler(msg: Message) -> None:
    chat = await Chat.objects.aget(chat_id=msg.chat.id)
    await chat.adelete()
    await msg.answer("Всмысле на 5 мин раньше решил уйти???")
    await asyncio.sleep(1)
    await msg.answer("УВОЛЕН!!!")
    await asyncio.sleep(1)
    await msg.answer("но карандашиком я тя запишу")
    

@dp.message(SlaveFilter())
async def auth_echo_handler(message: types.Message) -> None:
    await message.answer("Работать!!!")

@dp.message(NotSlaveFilter())
async def not_auth_echo_handler(message: Message) -> None:
    await message.answer("То есть всякие гадости писать мне есть время")
    await asyncio.sleep(1)
    await message.answer("А утроиться на завод нет?!")
    await asyncio.sleep(1)
    await message.answer("Бегом в отдел кадров /start.")
    

    
async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='Пойти на завод'
        ),
        BotCommand(
            command='quit',
            description='Уволиться'
        )
    ]
    
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def send_morning(bot: Bot):
    photo = FSInputFile("img/zavod.jpg") 
    target = time(8, 0, 0)
    MOSCOW_TZ = ZoneInfo('Europe/Moscow')
    async with redis.Redis(host='redis', port=6379, decode_responses=True) as r:
        while True:        
            today = await r.get("today")
            now = datetime.now(MOSCOW_TZ).time()
            if now >= target:
                if not today:
                    today = "1"
                    async for chat in Chat.objects.all():
                        await bot.send_photo(chat.chat_id, photo)
            else:
                today = ""
            await r.set("today", today)

            await asyncio.sleep(10)

async def main() -> None:
    # Настраиваем redis по умолчанию
    async with redis.Redis(host='redis', port=6379, decode_responses=True) as r:
        await r.set("today", "1")

    # Настройки бота
    TOKEN = os.getenv("BOT_TOKEN")
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    
    # Сначала зададим комманды для бота
    await set_commands(bot)
    # Теперь можно параллельно запустить самого бота и рассылку пикч
    await asyncio.gather(dp.start_polling(bot),
                         send_morning(bot))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
