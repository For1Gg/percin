import os
from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import types, Dispatcher
from telethon import TelegramClient
from database import Database
from dotenv import load_dotenv

load_dotenv()

storage = MemoryStorage()

channel_id = os.getenv("CHANNEL_ID")
admin_user_id = os.getenv("ADMIN_ID")

api_id = os.getenv("API_ID")
hash_id = os.getenv("HASH_ID")

client = TelegramClient('my_account_session', int(api_id), hash_id, flood_sleep_threshold=0)

bot = Bot(token=os.getenv("BOT_TOKEN"), parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

db = Database("database.sqlite")
