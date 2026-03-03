import asyncio
import re
from datetime import datetime
from telethon import utils, events
from config import client, bot, channel_id, db, admin_user_id
import logging

logger = logging.getLogger(__name__)

def get_triggers():
    """Получает список триггеров из БД"""
    triggers = db.fetchall("SELECT trigger FROM triggers")
    return [row[0].lower() for row in triggers]

@client.on(events.NewMessage)
async def message_handler(event):
    """Обрабатывает все новые сообщения"""
    try:
        # Проверяем что это группа или канал
        if not (event.is_group or event.is_channel):
            return
        
        # Получаем триггеры
        triggers = get_triggers()
        if not triggers:
            return
        
        # Проверяем текст сообщения
        if not event.raw_text:
            return
        
        text = event.raw_text.lower()
        
        # Ищем совпадения
        found = []
        for trigger in triggers:
            if trigger in text:
                found.append(trigger)
        
        if found:
            # Получаем информацию об отправителе
            sender = await event.get_sender()
            if sender and sender.bot:
                return
            
            sender_name = utils.get_display_name(sender) if sender else "Unknown"
            sender_username = sender.username if sender and sender.username else None
            
            # Получаем информацию о чате
            chat = await event.get_chat()
            chat_name = utils.get_display_name(chat)
            chat_username = chat.username if chat.username else None
            
            # Логируем в БД
            db.query("""
                INSERT INTO found_messages 
                (message_id, chat_id, sender_id, sender_name, sender_username, message_text, found_triggers, date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.message.id,
                chat.id,
                sender.id if sender else 0,
                sender_name,
                sender_username,
                event.raw_text[:500],
                ', '.join(found),
                datetime.now().isoformat()
            ))
            
            # Отправляем в канал
            message_text = f"""🔔 **НАЙДЕНО СОВПАДЕНИЕ!**

**Триггеры:** {', '.join(found)}

**Сообщение:**
{event.raw_text[:1000]}{'...' if len(event.raw_text) > 1000 else ''}

**Отправитель:**
👤 Имя: {sender_name}
🆔 ID: `{sender.id if sender else 0}`
📱 Юзернейм: {f'@{sender_username}' if sender_username else 'не указан'}

**Чат:**
💬 Название: {chat_name}
🔗 Ссылка: {f'https://t.me/{chat_username}' if chat_username else f'ID: {chat.id}'}

⏱ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            await bot.send_message(chat_id=channel_id, text=message_text, parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"Ошибка в обработчике: {e}")
        await bot.send_message(chat_id=admin_user_id, text=f"❌ Ошибка: {e}")

async def run_client():
    """Запуск клиента"""
    await client.run_until_disconnected()

async def run_userbot():
    """Запуск юзербота"""
    try:
        await asyncio.gather(
            asyncio.ensure_future(run_client())
        )
    except KeyboardInterrupt:
        print("⛔ Бот остановлен")
    except Exception as e:
        print(f"💥 Ошибка: {e}")
    finally:
        await client.disconnect()