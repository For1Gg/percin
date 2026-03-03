from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import db, admin_user_id, bot
import sqlite3

# ← ВОТ ЭТА СТРОКА БЫЛА ПОТЕРЯНА!
router = Router()

# ========== КЛАССЫ СОСТОЯНИЙ (FSM) ==========
class AddTrigger(StatesGroup):
    add_trigger = State()

class DeleteTrigger(StatesGroup):
    delete_trigger = State()

class AddChat(StatesGroup):
    add_chat = State()

class RemoveChat(StatesGroup):
    remove_chat = State()

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
def is_admin(user_id: int) -> bool:
    return str(user_id) == admin_user_id

async def set_default_commands():
    commands = [
        types.BotCommand(command="start", description="Запустить бота"),
        types.BotCommand(command="list_triggers", description="Список ключевых слов"),
        types.BotCommand(command="add_triggers", description="Добавить ключевые слова"),
        types.BotCommand(command="delete_trigger", description="Удалить ключевое слово"),
        types.BotCommand(command="list_chats", description="Список отслеживаемых чатов"),
        types.BotCommand(command="add_chat", description="Добавить чат"),
        types.BotCommand(command="remove_chat", description="Удалить чат"),
        types.BotCommand(command="stats", description="Статистика")
    ]
    await bot.set_my_commands(commands)

# ========== КОМАНДА START ==========
@router.message(Command("start"))
async def start_command(message: types.Message):
    if is_admin(message.from_user.id):
        await set_default_commands()
        await message.answer(
            "🔥 **TG PARSER BOT**\n\nКоманды ниже",
            parse_mode="Markdown"
        )
    else:
        await message.answer("❌ У вас нет прав для выполнения этой команды.")

# ========== ТРИГГЕРЫ ==========
@router.message(Command("add_triggers"))
async def add_trigger_start(message: types.Message, state: FSMContext):
    if is_admin(message.from_user.id):
        await message.answer(
            "📝 Введите через запятую ключевые слова\n"
            "Пример: нужен бот, лист, привет"
        )
        await state.set_state(AddTrigger.add_trigger)
    else:
        await message.reply("❌ Нет прав")

@router.message(AddTrigger.add_trigger)
async def add_trigger_process(message: types.Message, state: FSMContext):
    triggers = [t.strip() for t in message.text.split(',')]
    for trigger in triggers:
        db.query("INSERT INTO triggers (trigger) VALUES (?)", (trigger,))
        await message.answer(f"✅ Триггер **{trigger}** добавлен", parse_mode="Markdown")
    await state.clear()

@router.message(Command("list_triggers"))
async def list_triggers(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    
    triggers = db.fetchall("SELECT trigger FROM triggers")
    process_data = [item[0] for item in triggers]
    await message.answer(
        f"📋 **Список ключевых слов:**\n{', '.join(process_data)}",
        parse_mode="Markdown"
    )

@router.message(Command("delete_trigger"))
async def delete_trigger_start(message: types.Message, state: FSMContext):
    if is_admin(message.from_user.id):
        await message.answer("🗑 Введите слово которое хотите удалить")
        await state.set_state(DeleteTrigger.delete_trigger)
    else:
        await message.reply("❌ Нет прав")

@router.message(DeleteTrigger.delete_trigger)
async def delete_trigger_process(message: types.Message, state: FSMContext):
    trigger = message.text
    try:
        result = db.fetchone("SELECT * FROM triggers WHERE trigger=?", (trigger,))
        if result:
            db.query("DELETE FROM triggers WHERE trigger=?", (trigger,))
            await message.answer(f"✅ Ключевое слово **{trigger}** удалено", parse_mode="Markdown")
        else:
            await message.answer(f"❌ Ключевое слово **{trigger}** не найдено", parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
    finally:
        await state.clear()

# ========== ЧАТЫ ==========
@router.message(Command("list_chats"))
async def list_chats(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    
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
    await message.answer(text, parse_mode="Markdown")

@router.message(Command("add_chat"))
async def add_chat_start(message: types.Message, state: FSMContext):
    if is_admin(message.from_user.id):
        await message.answer(
            "➕ Введите username чата или ID\n"
            "Пример: @durov или -100123456789"
        )
        await state.set_state(AddChat.add_chat)
    else:
        await message.reply("❌ Нет прав")

@router.message(AddChat.add_chat)
async def add_chat_process(message: types.Message, state: FSMContext):
    chat_input = message.text.strip()
    await message.answer(f"🔍 Проверяю чат {chat_input}...")
    
    try:
        # Убираем @ если есть
        if chat_input.startswith('@'):
            chat_input = chat_input[1:]
        
        # Пытаемся получить информацию о чате через Telethon
        from config import client
        entity = await client.get_entity(chat_input)
        
        # Сохраняем в базу
        from config import db
        db.query(
            "INSERT INTO monitored_chats (chat_id, chat_title, chat_username, chat_type) VALUES (?, ?, ?, ?)",
            (entity.id, entity.title or "Без названия", getattr(entity, 'username', None), 'group' if entity.megagroup else 'channel')
        )
        
        await message.answer(f"✅ Чат **{entity.title}** добавлен в отслеживание!\nID: `{entity.id}`", parse_mode="Markdown")
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: не удалось найти чат {chat_input}\n{str(e)}")
    
    await state.clear()

@router.message(Command("remove_chat"))
async def remove_chat_start(message: types.Message, state: FSMContext):
    if is_admin(message.from_user.id):
        await message.answer("🗑 Введите username чата или ID для удаления")
        await state.set_state(RemoveChat.remove_chat)
    else:
        await message.reply("❌ Нет прав")

@router.message(RemoveChat.remove_chat)
async def remove_chat_process(message: types.Message, state: FSMContext):
    # TODO: реализовать удаление
    await state.clear()

# ========== СТАТИСТИКА ==========
@router.message(Command("stats"))
async def show_stats(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    
    triggers_count = db.fetchone("SELECT COUNT(*) FROM triggers")[0]
    chats_count = db.fetchone("SELECT COUNT(*) FROM monitored_chats")[0]
    messages_count = db.fetchone("SELECT COUNT(*) FROM found_messages")[0]
    
    stats = f"""📊 **СТАТИСТИКА**

🔑 Ключевых слов: {triggers_count}
💬 Отслеживаемых чатов: {chats_count}
📨 Найдено сообщений: {messages_count}

⚡ Бот работает через твой аккаунт
🔥 Мониторинг всех чатов где ты есть"""
    
    await message.answer(stats, parse_mode="Markdown")
