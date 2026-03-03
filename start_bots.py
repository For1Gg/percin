from aiogram.utils import executor
from config import dp, db, client
import logging
import bot
import userbot
import asyncio
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def on_startup(dp):
    """Действия при запуске"""
    db.create_tables()
    await client.start()
    print("="*60)
    print("🚀 TG PARSER BOT ЗАПУЩЕН")
    print("="*60)
    print(f"👑 Админ: {os.getenv('ADMIN_ID')}")
    print(f"🤖 Бот работает через твой аккаунт")
    print("🔥 Мониторинг запущен, *****!")
    print("="*60)

async def on_shutdown(dp):
    """Действия при остановке"""
    await client.disconnect()
    print("⛔ Бот остановлен")

if __name__ == "__main__":
    executor.start_polling(dp, on_shutdown=on_shutdown, on_startup=on_startup)