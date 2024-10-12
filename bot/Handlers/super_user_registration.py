import logging
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from datetime import datetime
from bot.bot import dp
from bot.bd import new_sup_user
from bot.Keyboards import KeyBoards
from bot.Middleware.secure_middleware import rate_limit
import pymorphy3


morph = pymorphy3.MorphAnalyzer()

logger = logging.getLogger("bot.super_user_registration")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)


class SuperUserRegister(StatesGroup):
    waiting_for_name = State()
    waiting_for_birthday = State()

class SuperUserRegistration:
    @rate_limit(3, 'NewB')
    @dp.message_handler(Text(equals="Добавить день рождения", ignore_case=True))
    @staticmethod
    async def add_birthday_button_pressed(message: types.Message, role:str):
        user_id = message.from_user.id
        if role == "user":
            await message.reply("Для доступа к этой функции вам необходима подписка уровня Super_User")
            logger.info(f"Пользователь с ID {user_id} попытался добавить день рождения.")
            return
        else:
            await message.reply("Введите имя:", reply_markup=KeyBoards.cancel_keyboard)
            await SuperUserRegister.waiting_for_name.set()
            logger.info(f"Начата регистрация дня рождения для суперпользователя {user_id}.")

    @rate_limit(3, 'Cancel')
    @dp.message_handler(Text(equals="Отменить", ignore_case=True), state="*")
    @staticmethod
    async def cancel_registration(message: types.Message, state: FSMContext, role: str):
        current_state = await state.get_state()
        await state.update_data(role=role)
        if current_state is not None:
            await state.finish()
            await message.reply("Отмена", reply_markup=KeyBoards.get_keyboard(role))
            logger.info(f"Пользователь {message.from_user.id} отменил регистрацию.")
        else:
            await message.reply("Отмена операции", reply_markup=KeyBoards.get_keyboard((role)))


    @dp.message_handler(state=SuperUserRegister.waiting_for_name, content_types=types.ContentTypes.TEXT)
    @staticmethod
    @dp.message_handler(state=SuperUserRegister.waiting_for_name, content_types=types.ContentTypes.TEXT)
    @staticmethod
    async def process_name(message: types.Message, state: FSMContext):
        name = message.text.strip()
        user_id = message.from_user.id
        if not name:
            await message.reply("Имя не может быть пустым. Пожалуйста, введите ваше имя:",
                                reply_markup=KeyBoards.cancel_keyboard)
            logger.warning(f"Пользователь {user_id} отправил пустое имя.")
            return
        parsed = morph.parse(name)
        if not parsed:
            await message.reply("Пожалуйста, введите осмысленное имя:", reply_markup=KeyBoards.cancel_keyboard)
            logger.warning(f"Пользователь {user_id} отправил нераспознаваемое имя: '{name}'.")
            return
        is_name = any('Name' in p.tag for p in parsed)
        if not is_name:
            await message.reply("Пожалуйста, введите корректное имя:", reply_markup=KeyBoards.cancel_keyboard)
            logger.warning(f"Пользователь {user_id} отправил некорректное имя: '{name}'.")
            return
        await state.update_data(name=name)
        logger.info(f"Пользователь {user_id} ввел имя: {name}.")
        await message.reply("Введите вашу дату рождения в формате ДД.ММ.ГГГГ:", reply_markup=KeyBoards.cancel_keyboard)
        await SuperUserRegister.waiting_for_birthday.set()

    @dp.message_handler(state=SuperUserRegister.waiting_for_birthday, content_types=types.ContentTypes.TEXT)
    @staticmethod
    async def process_birthday(message: types.Message, state: FSMContext, role:str):
        birthday_str = message.text.strip()
        try:
            birthday = datetime.strptime(birthday_str, "%d.%m.%Y").date()
        except ValueError:
            await (message.reply("Некорректный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ:", reply_markup = KeyBoards.cancel_keyboard))
            logger.warning(f"Пользователь {message.from_user.id} ввел некорректную дату: '{birthday_str}'.")
            return
        user_data = await state.get_data()
        name = user_data.get("name")
        super_user_id = message.from_user.id
        new_sup_user(name=name, super_user_id = super_user_id, birthday_date=birthday)
        await (message.reply(f"Вы успешно внесли день рождения!\nИмя: {name}\nДата рождения:"f" {birthday.strftime('%d.%m.%Y')}",reply_markup=KeyBoards.get_keyboard(role)))
        logger.info(f"Суперпользователь {super_user_id} успешно внес свой день рождения '{name}' и датой рождения {birthday}.")
        await state.finish()