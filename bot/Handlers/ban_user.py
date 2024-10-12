from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot.bot import dp
from bot.bd import new_banned_user
from bot.Middleware.secure_middleware import rate_limit
from bot.Keyboards import KeyBoards
from bot.Utils import RecordLogs


class BanRegister(StatesGroup):
    waiting_for_user_id = State()


class BanRegistration:
    @rate_limit(3, 'Ban User')
    @dp.message_handler(text="Забанить пользователя")
    async def admin_ban(message: types.Message, role: str):
        if role != 'admin':
            await message.reply("У вас нет доступа к этому разделу.", reply_markup=KeyBoards.get_keyboard(role))
            RecordLogs.log_user_action(message.from_user.id, "попытался получить доступ к списку пользователей.")
        else:
            await BanRegister.waiting_for_user_id.set()
            await message.reply("Введите ID пользователя для бана:", reply_markup=KeyBoards.cancel_keyboard)

    @dp.message_handler(state=BanRegister.waiting_for_user_id, content_types=types.ContentTypes.TEXT)
    @staticmethod
    async def process_user_id(message: types.Message, state: FSMContext):
        try:
            banned_id = int(message.text.strip())
        except ValueError:
            await message.reply("Неверный формат ID.")
            return
        new_banned_user(banned_id)
        await message.reply(f"Пользователь с ID {banned_id} добавлен в бан-лист.")
        await state.finish()
