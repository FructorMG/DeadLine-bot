import logging
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from datetime import datetime
from bot.bot import dp
from bot.bd import new_sup_user
from bot.Keyboards import KeyBoards

logger = logging.getLogger("bot.super_user_registration")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

class SuperUserRegister(StatesGroup):
    waiting_for_name = State()
    waiting_for_birthday = State()

class SuperUserRegistration:

    @staticmethod
    @dp.message_handler(Text(equals="Добавить день рождения", ignore_case=True))
    async def add_birthday_button_pressed(message: types.Message, state: FSMContext, role: str):
        user_id = message.from_user.id
        await message.reply("Введите имя:", reply_markup=KeyBoards.cansel_keyboard)
        await SuperUserRegister.waiting_for_name.set()
        logger.info(f"Начата регистрация дня рождения для суперпользователя {user_id}.")

    @staticmethod
    @dp.message_handler(Text(equals="Отменить", ignore_case=True))
    async def cancel_registration(message: types.Message, state: FSMContext):
        current_state = await state.get_state()
        if current_state is not None:
            await state.finish()
            await message.reply(
                "До встречи! Я всегда тут, просто нажми /start",
                reply_markup=types.ReplyKeyboardRemove()
            )
            logger.info(f"Пользователь {message.from_user.id} отменил регистрацию.")
        else:
            await message.reply(
                "До встречи! Я всегда тут, просто нажми /start",
                reply_markup=types.ReplyKeyboardRemove()
            )

    @staticmethod
    @dp.message_handler(state=SuperUserRegister.waiting_for_name, content_types=types.ContentTypes.TEXT)
    async def process_name(message: types.Message, state: FSMContext):
        name = message.text.strip()
        if not name:
            await message.reply("Имя не может быть пустым. Пожалуйста, введите ваше имя:",reply_markup=KeyBoards.cancel_keyboard())
            return
        await state.update_data(name=name)
        await message.reply("Введите рождения в формате ДД.ММ.ГГГГ:")
        await SuperUserRegister.waiting_for_birthday.set()
        logger.info(f"Пользователь {message.from_user.id} ввел имя: {name}.")

    @staticmethod
    @dp.message_handler(state=SuperUserRegister.waiting_for_birthday, content_types=types.ContentTypes.TEXT)
    async def process_birthday(message: types.Message, state: FSMContext, role:str):
        birthday_str = message.text.strip()
        try:
            birthday = datetime.strptime(birthday_str, "%d.%m.%Y").date()
        except ValueError:
            await message.reply("Некорректный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ:", reply_markup=KeyBoards.cancel_keyboard())
            logger.warning(f"Пользователь {message.from_user.id} ввел некорректную дату: '{birthday_str}'.")
            return
        user_data = await state.get_data()
        name = user_data.get("name")
        super_user_id = message.from_user.id
        new_sup_user(name=name, super_user_id = super_user_id, birthday_date=birthday)
        await message.reply(
                    f"Вы успешно внесли день рождения!\nИмя: {name}\nДата рождения: {birthday.strftime('%d.%m.%Y')}",
                    reply_markup=KeyBoards.get_keyboard(role)
                )
        logger.info(f"Суперпользователь {super_user_id} успешно внес свой день рождения '{name}' и датой рождения {birthday}.")
        await state.finish()