import logging
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from datetime import datetime
from bot.bot import dp
from bot.bd import user_exists, new_user
from bot.Keyboards import KeyBoards
from bot.Middleware.secure_middleware import rate_limit

import pymorphy3

# Инициализация MorphAnalyzer
morph = pymorphy3.MorphAnalyzer()

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class UserRegister(StatesGroup):
    waiting_for_name = State()
    waiting_for_birthday = State()


class UserRegistration:
    @rate_limit(3, 'start')
    @dp.message_handler(commands=["start"])
    @staticmethod
    async def send_welcome(message: types.Message):
        await message.reply("Привет! Я бот для уведомлений о днях рождения.\nДля продолжения необходимо пройти регистрацию. Продолжить?",reply_markup=KeyBoards.registration_keyboard)

    @rate_limit(3, 'Yes')
    @dp.message_handler(Text(equals="Да", ignore_case=True))
    @staticmethod
    async def start_registration(message: types.Message, state: FSMContext, role:str):
        user_id = message.from_user.id
        await state.update_data(role=role)
        if user_exists(user_id):
            await message.reply("Вы уже зарегистрированы.", reply_markup=KeyBoards.get_keyboard(role))
            logger.info(f"Пользователь {user_id} попытался зарегистрироваться повторно.")
            return

        await message.reply("Введите ваше имя:", reply_markup=KeyBoards.cancel_reg_keyboard)
        await UserRegister.waiting_for_name.set()
        logger.info(f"Начата регистрация для пользователя {user_id}.")

    @rate_limit(3, 'No')
    @dp.message_handler(Text(equals="Нет", ignore_case=True))
    @staticmethod
    async def handle_no_response(message: types.Message):
        await message.reply("До встречи! Я всегда тут, просто нажми /start",reply_markup=types.ReplyKeyboardRemove())
        logger.info(f"Пользователь {message.from_user.id} отменил регистрацию, выбрав 'Нет'.")

    @rate_limit(3, 'CancelRegistation')
    @dp.message_handler(Text(equals="Отменить регистрацию", ignore_case=True),state="*")
    @staticmethod
    async def cancel_registration(message: types.Message, state: FSMContext):
        current_state = await state.get_state()
        if current_state is not None:
            await state.finish()
            await message.reply("До встречи! Я всегда тут, просто нажми /start",reply_markup=types.ReplyKeyboardRemove())
            logger.info(f"Пользователь {message.from_user.id} отменил регистрацию.")
        else:
            await message.reply("До встречи! Я всегда тут, просто нажми /start",reply_markup=types.ReplyKeyboardRemove() )
    @dp.message_handler(state=UserRegister.waiting_for_name, content_types=types.ContentTypes.TEXT)
    @staticmethod
    async def process_name(message: types.Message, state: FSMContext):
        name = message.text.strip()
        user_id = message.from_user.id
        if not name:
            await message.reply("Имя не может быть пустым. Пожалуйста, введите ваше имя:",reply_markup=KeyBoards.cancel_reg_keyboard)
            logger.warning(f"Пользователь {user_id} отправил пустое имя.")
            return
        parsed = morph.parse(name)
        if not parsed:
            await message.reply(
                "Пожалуйста, введите осмысленное имя:",
                reply_markup=KeyBoards.cancel_reg_keyboard
            )
            logger.warning(f"Пользователь {user_id} отправил нераспознаваемое имя: '{name}'.")
            return
        is_name = any('Name' in p.tag for p in parsed)
        if not is_name:
            await message.reply("Пожалуйста, введите корректное имя:",reply_markup=KeyBoards.cancel_reg_keyboard)
            logger.warning(f"Пользователь {user_id} отправил некорректное имя: '{name}'.")
            return

        await state.update_data(name=name)
        logger.info(f"Пользователь {user_id} ввел имя: {name}.")
        await message.reply("Введите вашу дату рождения в формате ДД.ММ.ГГГГ:", reply_markup=KeyBoards.cancel_reg_keyboard)
        await UserRegister.waiting_for_birthday.set()

    @dp.message_handler(state=UserRegister.waiting_for_birthday, content_types=types.ContentTypes.TEXT)
    @staticmethod
    async def process_birthday(message: types.Message, state: FSMContext, role:str ):
        birthday_str = message.text.strip()
        user_id = message.from_user.id
        try:
            birthday = datetime.strptime(birthday_str, "%d.%m.%Y").date()
        except ValueError:
            await message.reply("Некорректный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ:", reply_markup=KeyBoards.cancel_reg_keyboard)
            logger.warning(f"Пользователь {user_id} ввел некорректную дату: '{birthday_str}'.")
            return
        user_data = await state.get_data()
        name = user_data.get("name")
        user_username = message.from_user.username or "unknown"
        if user_exists(user_id):
            await message.reply("Вы уже зарегистрированы.", reply_markup=KeyBoards.get_keyboard(role))
            logger.info(f"Пользователь {user_id} попытался зарегистрироваться повторно.")
        else:
            new_user(
                name=name,
                user_id=user_id,
                birthday_date=birthday,
                user_username=user_username
            )
            await message.reply(f"Регистрация завершена!\nИмя: {name}\nДата рождения: {birthday.strftime('%d.%m.%Y')}",reply_markup=KeyBoards.get_keyboard(role))
            logger.info(f"Пользователь {user_id} успешно зарегистрирован с именем '{name}' и датой рождения {birthday}.")
        await state.finish()
