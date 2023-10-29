from api.models import Chat

from zavodik.settings import API_ID, API_HASH, BOT_TOKEN

import asyncio
from pyrogram.handlers import MessageHandler
import pyrogram.types as types
from pyrogram import Client, compose, filters, idle
from pyrogram.enums import UserStatus

from apscheduler.schedulers.asyncio import AsyncIOScheduler


from ._sync import async_to_sync

# Клиент - человек, для просмотра статуса пользователя
man = Client("man",
             api_id=API_ID,
             api_hash=API_HASH)

# Клиент - бот, для взаимодействия с пользователями
bot = Client("bot",
             api_id=API_ID,
             api_hash=API_HASH,
             bot_token=BOT_TOKEN)

scheduler = AsyncIOScheduler()

async def getChat(chat_id):
    try:
        chat = await Chat.objects.aget(chat_id=chat_id)
    except Chat.DoesNotExist:
            return None
    return chat

async def isSlave(chat_id):
    try:
        chat = await Chat.objects.aget(chat_id=chat_id)
    except Chat.DoesNotExist:
            return False
    return True

def notify(chat_id):
    async def check():
        # получаем поле чата из БД
        chat = await getChat(chat_id)
        
        if chat is None:
            try:
                scheduler.remove_job(str(chat_id))
            finally:
                return
                
        # Определяем текущий статус пользователя
        cur_status: UserStatus = (await man.get_users(chat.chat_id)).status
        chat.is_online = (cur_status == UserStatus.ONLINE)
        
        # Если пользователь онлайн
        if chat.is_online:
            # и мы еще не отправляли ему уведомление
            if not chat.is_send:
                # отправляем уведомление
                await bot.send_message(chat.chat_id, "Работать!!!")
                # Поднимаем фоаг что отправили уведомление
                chat.is_send = True
        else:
            # Мы оффлайн, значит уведомление никакое не отправляли
            chat.is_send = False
        
        # Сохраняем изменения в базу данных 
        try:
            await chat.asave()
        except:
            pass
    
    return check

@bot.on_message(filters.command(["start"]))
async def start_handler(client, msg: types.Message):
    try:
        myChat: Chat =  await Chat.objects.acreate(chat_id=msg.chat.id)
        await myChat.asave()
    except:
        await msg.reply("Ты уже в рабстве")
        await asyncio.sleep(1)
        await msg.reply("Ну ладно, так уж и быть, работать!!!")
    else:
        await msg.reply("Я добавил тебя в список пидорасов")
        await asyncio.sleep(1)
        await msg.reply("Теперь каждый раз, когда ты будешь online\nя напомню что ты должен делать")
        await asyncio.sleep(2)
        await msg.reply("А теперь, работать!!!")
        # добавляем проверку на статус пользователя каждые 5 секунд
        scheduler.add_job(notify(msg.chat.id), 'interval', seconds=5, id=str(myChat.chat_id))
    

@bot.on_message(filters.command(["quit"]))
async def quit_handler(client, msg: types.Message):
    try:
        chat = await Chat.objects.aget(chat_id=msg.chat.id)
        await chat.adelete()
    except Chat.DoesNotExist:
        await msg.reply("Пиздюк сначала отработай смену на заводе /start")
    else:
        await msg.reply("В картотеке, тебя больше нет")
        await asyncio.sleep(1)
        await msg.reply("Но это не означает, что можно не работать!!!")
        await asyncio.sleep(1)
        await msg.reply("работать на удалёнке!!!")
    
    # Дальше пытаемся убрать проверку на статус пользователя в sheduler
    try:
        scheduler.remove_job(str(msg.chat.id))
    finally:
        return

@bot.on_message(filters.text & filters.private)
async def simple_handler(client: Client, msg: types.Message):
    # Отправьте сообщение пользователю с ID 12345, используя второго бота
    # artem = await man.get_users(182826395)
    # await msg.reply_text(f'Артем сейчас {artem.status}')
    if (await isSlave(msg.chat.id)):
        await msg.reply("Лучше бы ты был на заводе")
        await msg.reply("РАБОТАТЬ!!!")
    else:
        await msg.reply("Вот пишешь пишешь мне всякие гадости")
        await asyncio.sleep(1)
        await msg.reply("а часики-то тикают!!!")
        await asyncio.sleep(1)
        await msg.reply("Пора устроиться на завод /start")

@async_to_sync
async def start_bot():
    await man.start()
    await bot.start()
 
    # scheduler.add_job(lololol, 'interval', seconds=5)
    scheduler.start()
    
    await idle()

    await bot.stop()
    await man.start()