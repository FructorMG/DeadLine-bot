import logging
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from datetime import datetime
from bot.bot import dp
from bot.bd import new_user, get_all_users, get_all_birthdays, user_exists
from bot.Keyboards import KeyBoards
from bot.config import config
from bot.Utils.Record_Logs import RecordLogs

logger = logging.getLogger("bot.handlers")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class RegisterUser(StatesGroup):
    waiting_for_name = State()
    waiting_for_birthday = State()

class Handlers:
    @dp.message_handler(commands = ['start'])
    @staticmethod
    async def send_welcome(message: types.Message, state: FSMContext, role: str = 'user'):
        await message.reply("Привет! Я бот для уведомлений о днях рождения.\n Для продолжения необходимо пройти регистрацию. Продолжить?",
                            reply_markup = KeyBoards.registration_keyboard)
        logger.info(f"Пользователь {message.from_user.id} вызвал команду /start и получил запрос на регистрацию с ролью {role}.")

    @dp.message_handler(Text(equals = 'Да', ignore_case = True))
    @staticmethod
    async def start_registration(message: types.Message, state: FSMContext, role: str = 'user'):
        user_id = message.from_user.id
        username = message.from_user.username or "unknown"
        if user_exists(user_id):
            await message.reply("Вы уже зарегистрированы.", reply_markup=KeyBoards.get_keyboard(role))
            logger.info(f"Пользователь {user_id} попытался зарегистрироваться повторно.")
            return

        await message.reply("Введите ваше имя:")
        await RegisterUser.waiting_for_name.set()
        logger.info(f"Начата регистрация для пользователя {user_id}.")

    @dp.message_handler(Text(equals = 'Нет', ignore_case = True))
    @staticmethod
    async def cancel_registration_start(message: types.Message, state: FSMContext, role: str = 'user'):
        await message.reply("Регистрация отменена.", reply_markup=KeyBoards.get_keyboard(role))
        logger.info(f"Пользователь {message.from_user.id} отменил регистрацию на старте.")

    @dp.message_handler(commands = ['cancel'])
    @dp.message_handler(Text(equals = 'Отмена', ignore_case = True))
    @staticmethod
    async def cancel_registration(message: types.Message, state: FSMContext, role: str):
        current_state = await state.get_state()
        if current_state is None:
            await message.reply("Нет активной регистрации.", reply_markup = KeyBoards.get_keyboard(role))
            return
        await state.finish()
        await message.reply("Регистрация отменена.", reply_markup = KeyBoards.get_keyboard(role))
        logger.info(f"Пользователь {message.from_user.id} отменил регистрацию.")

    @dp.message_handler(state = RegisterUser.waiting_for_name, content_types = types.ContentTypes.TEXT)
    @staticmethod
    async def process_name(message: types.Message, state: FSMContext):
        name = message.text.strip()
        if not name:
            await message.reply("Имя не может быть пустым. Пожалуйста, введите ваше имя:")
            return
        await state.update_data(name = name)
        await message.reply("Введите вашу дату рождения в формате ДД.ММ.ГГГГ:")
        await RegisterUser.waiting_for_birthday.set()
        logger.info(f"Пользователь {message.from_user.id} ввел имя: {name}.")

    @dp.message_handler(state = RegisterUser.waiting_for_birthday, content_types = types.ContentTypes.TEXT)
    @staticmethod
    async def process_birthday(message: types.Message, state: FSMContext, role: str = 'user'):
        birthday_str = message.text.strip()
        try:
            birthday = datetime.strptime(birthday_str, '%d.%m.%Y').date()
        except ValueError:
            await message.reply("Некорректный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ:")
            logger.warning(f"Пользователь {message.from_user.id} ввел некорректную дату: '{birthday_str}'.")
            return
        user_data = await state.get_data()
        name = user_data.get('name')
        user_id = message.from_user.id
        user_username = message.from_user.username or "unknown"
        if user_exists(user_id):
            await message.reply("Вы уже зарегистрированы.", reply_markup = KeyBoards.get_keyboard(role))
            logger.info(f"Пользователь {user_id} попытался зарегистрироваться повторно.")
        else:
            new_user(name = name, user_id = user_id, birthday_date = birthday, user_username = user_username)
            await message.reply(f"Регистрация завершена!\nИмя: {name}\nДата рождения: {birthday.strftime('%d.%m.%Y')}", reply_markup = KeyBoards.get_keyboard(role)
            )
            logger.info(f"Пользователь {user_id} успешно зарегистрирован с именем '{name}' и датой рождения {birthday}.")
        await state.finish()

    @dp.message_handler(text = 'Помощь')
    @staticmethod
    async def support(message: types.Message, role: str = 'user'):
        assistants = ", ".join([str(id_) for id_ in config.assistants_list])
        await message.reply(f'Если вы заметили ошибку или хотите поделиться своими пожеланиями по поводу бота, пожалуйста, свяжитесь с {assistants}.',
                            reply_markup = KeyBoards.get_keyboard(role)
        )
        logger.info(f"Пользователь {message.from_user.id} запросил помощь.")

    @dp.message_handler(text = 'Добавить день рождения')
    @staticmethod
    async def add_birthday(message: types.Message, role: str):
        if role == 'super_users':
            await message.reply("Функция добавления дня рождения пока не реализована.", reply_markup = KeyBoards.get_keyboard(role))
            logger.info(f"Суперпользователь {message.from_user.id} попытался добавить день рождения.")
        else:
            await message.reply("Для доступа к этому разделу необходима подписка уровня SUPER_USER.", reply_markup=KeyBoards.get_keyboard(role))
            logger.warning(f"Пользователь {message.from_user.id} без прав пытался добавить день рождения.")

    @dp.message_handler(text='Список дней рождений')
    @staticmethod
    async def birthdays_list(message: types.Message,role: str):
        print(role)
        logger.info(f"Пользователь {message.from_user.id} (роль {role}) запросил список дней рождений.")
        RecordLogs.log_user_action(message.from_user.id, "запросил список дней рождений.")
        try:
            await get_all_birthdays(message)
        except Exception as e:
            # await message.reply(f"Произошла ошибка: {e}", reply_markup=KeyBoards.get_keyboard(role))
            logger.error(f"У пользователя {message.from_user.id} произошла ошибка: {e}")
            RecordLogs.log_user_action(message.from_user.id, f"произошла ошибка: {e}")

    @dp.message_handler(text='Список пользователей')
    @staticmethod
    async def users_list(message: types.Message,role: str):
        if role != 'admin':
            await message.reply("У вас нет доступа к этому разделу.", reply_markup = KeyBoards.get_keyboard(role))
            logger.warning(f"Пользователь {message.from_user.id} попытался получить доступ к списку пользователей.")
            RecordLogs.log_user_action(message.from_user.id, "попытался получить доступ к списку пользователей.")
            return
        logger.info(f"Администратор {message.from_user.id} запросил список пользователей.")
        RecordLogs.log_admin_action(message.from_user.id, "запросил список пользователей.")
        try:
            await get_all_users(message)
        except FileNotFoundError:
            await message.reply("Файл users.csv не найден.", reply_markup = KeyBoards.get_keyboard(role))
            logger.error("Файл users.csv не найден.")
        except Exception as e:
            await message.reply(f"Произошла ошибка: {e}", reply_markup = KeyBoards.get_keyboard(role))
            logger.error(f"У администратора {message.from_user.id} произошла ошибка: {e}")
            RecordLogs.log_admin_action(message.from_user.id, "произошла ошибка")

