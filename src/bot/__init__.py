import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import TELEGRAM_BOT_TOKEN
from src.bot.handlers import user_router, admin_router
from src.bot.handlers.user import ADMIN_MESSAGES

bot = Bot(TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
dp.include_routers(user_router, admin_router)

async def run_bot():
    async def messages_worker():
        while True:
            await asyncio.sleep(3600)
            ADMIN_MESSAGES.clear()
            print('cleared')

    asyncio.create_task(messages_worker())
    await bot.delete_webhook(True)
    await dp.start_polling(bot)
