import sqlite3
from config import db, dp, admin_user_id
from aiogram.dispatcher import FSMContext
from aiogram import types
from state import AddTrigger, DeleteTrigger, AddChat, RemoveChat

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    user_id = str(message.from_user.id)

    if user_id == admin_user_id:
        await set_default_commands(dp)
        await message.answer(f"🔥 **TG PARSER BOT**\n\nКоманды ниже", parse_mode=types.ParseMode.MARKDOWN)
    else:
        await message.answer("❌ У вас нет прав для выполнения этой команды.")

async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("list_triggers", "Список ключевых слов"),
        types.BotCommand("add_triggers", "Добавить ключевые слова"),
        types.BotCommand("delete_trigger", "Удалить ключевое слово"),
        types.BotCommand("list_chats", "Список отслеживаемых чатов"),
        types.BotCommand("add_chat", "Добавить чат для отслеживания"),
        types.BotCommand("remove_chat", "Удалить чат"),
        types.BotCommand("stats", "Статистика")
    ])

# ========== ТРИГГЕРЫ ==========
@dp.message_handler(commands=['add_triggers'])
async def add_trigger(message: types.Message):
    user_id = str(message.from_user.id)
    if user_id == admin_user_id:
        await message.answer("📝 Введите через запятую ключевые слова\nПример: нужен бот, лист, привет")
        await AddTrigger.add_trigger.set()
    else:
        await message.reply("❌ Нет прав")

@dp.message_handler(state=AddTrigger.add_trigger)
async def trigger_set(message: types.Message, state: FSMContext):
    triggers = message.text.split(', ')
    for trigger in triggers:
        db.query("INSERT INTO triggers (trigger) VALUES (?)", (trigger.strip(),))
        await message.answer(f"✅ Триггер **{trigger}** добавлен", parse_mode=types.ParseMode.MARKDOWN)
    await state.finish()

@dp.message_handler(commands=['list_triggers'])
async def list_triggers(message: types.Message):
    triggers = db.fetchall("SELECT trigger FROM triggers")
    process_data = [item[0] for item in triggers]
    await message.answer(f"📋 **Список ключевых слов:**\n{', '.join(process_data)}", parse_mode=types.ParseMode.MARKDOWN)

@dp.message_handler(commands=['delete_trigger'])
async def process_delete(message: types.Message):
    await message.answer("🗑 Введите слово которое хотите удалить")
    await DeleteTrigger.delete_trigger.set()

@dp.message_handler(state=DeleteTrigger.delete_trigger)
async def delete_trigger(message: types.Message, state: FSMContext):
    trigger = message.text
    try:
        result = db.fetchone("SELECT * FROM triggers WHERE trigger=?", (trigger,))
        if result:
            db.query("DELETE FROM triggers WHERE trigger=?", (trigger,))
            await message.answer(f"✅ Ключевое слово **{trigger}** удалено", parse_mode=types.ParseMode.MARKDOWN)
            await state.finish()
        else:
            await message.answer(f"❌ Ключевое слово **{trigger}** не найдено", parse_mode=types.ParseMode.MARKDOWN)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
        await state.finish()

# ========== ЧАТЫ ==========
@dp.message_handler(commands=['list_chats'])
async def list_chats(message: types.Message):
    chats = db.fetchall("SELECT chat_title, chat_username, chat_id FROM monitored_chats")
    if not chats:
        await message.answer("📭 Нет отслеживаемых чатов")
        return
    
    text = "📋 **Отслеживаемые чаты:**\n\n"
    for chat in chats:
        text += f"• **{chat[0]}**\n"
        if chat[1]:
            text += f"  @{chat[1]}\n"
        else:
            text += f"  ID: `{chat[2]}`\n"
    await message.answer(text, parse_mode=types.ParseMode.MARKDOWN)

@dp.message_handler(commands=['add_chat'])
async def add_chat(message: types.Message):
    await message.answer("➕ Введите username чата или ID\nПример: @durov или -100123456789")
    await AddChat.add_chat.set()

@dp.message_handler(state=AddChat.add_chat)
async def process_add_chat(message: types.Message, state: FSMContext):
    chat_input = message.text.strip()
    await message.answer(f"🔍 Проверяю чат {chat_input}...")
    # Тут будет проверка через Telethon
    await state.finish()

@dp.message_handler(commands=['remove_chat'])
async def remove_chat(message: types.Message):
    await message.answer("🗑 Введите username чата или ID для удаления")
    await RemoveChat.remove_chat.set()

# ========== СТАТИСТИКА ==========
@dp.message_handler(commands=['stats'])
async def show_stats(message: types.Message):
    triggers_count = db.fetchone("SELECT COUNT(*) FROM triggers")[0]
    chats_count = db.fetchone("SELECT COUNT(*) FROM monitored_chats")[0]
    messages_count = db.fetchone("SELECT COUNT(*) FROM found_messages")[0]
    
    stats = f"""📊 **СТАТИСТИКА**

🔑 Ключевых слов: {triggers_count}
💬 Отслеживаемых чатов: {chats_count}
📨 Найдено сообщений: {messages_count}

⚡ Бот работает через твой аккаунт
🔥 Мониторинг всех чатов где ты есть"""
    
    await message.answer(stats, parse_mode=types.ParseMode.MARKDOWN)