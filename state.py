from aiogram.dispatcher.filters.state import StatesGroup, State

class AddTrigger(StatesGroup):
    add_trigger = State()

class DeleteTrigger(StatesGroup):
    delete_trigger = State()

class AddChat(StatesGroup):
    add_chat = State()

class RemoveChat(StatesGroup):
    remove_chat = State()