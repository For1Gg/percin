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
