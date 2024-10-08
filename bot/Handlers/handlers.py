import logging
from aiogram import types
from bot.bot import dp
from bot.Keyboards import KeyBoards
from bot.Utils.csv_utils import read_csv_data
from bot.Utils.Record_Logs import RecordLogs
from bot.config import config
from bot.bd.bd import new_user, get_all_users, get_all_birthdays

logger = logging.getLogger("bot")
class Handlers:
    @dp.message_handler(commands=['start'])
    @staticmethod
    async def send_welcome(message: types.Message):
        #role = getattr(message, 'role', 'user')
        #user_id = str(message.from_user.id)
        #username = message.from_user.username
        #logger.info(f"Пользователь {user_id} вызвал команду /start.")
        await message.reply("Привет! Я бот для уведомлений о днях рождения.")
        # В этот момент должно собираться имя + user_id.
        #new_user(username, user_id)
        #Создать клавиатуру выбора да, нет.(+)
        await message.reply("Для продолжения необходимо пройти регистрацию. Продолжить?", reply_markup=KeyBoards.registration_keyboard)
    @dp.message_handler(text = 'Да')
    @staticmethod
    async def start_registration(message:types.Message):
        await message.answer(f'Начало регистрации')
        user_id = str(message.from_user.id)
        username = message.from_user.username
        new_user(username, user_id)
        #Дописать сбор дня рождения и ФИО.


    @dp.message_handler(text='Помощь')
    @staticmethod
    async def support(message: types.Message):
        role = getattr(message, 'role', 'user')
        assistants = ", ".join([str(id_) for id_ in config.assistants_list])
        await message.reply(
            f'Если вы заметили ошибку или хотите поделиться своими пожеланиями по поводу бота, пожалуйста, свяжитесь с {assistants}.',
            reply_markup=KeyBoards.get_keyboard(role)
        )

    @dp.message_handler(text='Добавить день рождения')
    @staticmethod
    async def add_birthday(message: types.Message):
        role = getattr(message, 'role', 'user')
        if role == 'super_users':
            await message.reply("Функция добавления дня рождения пока не реализована.", reply_markup=KeyBoards.get_keyboard(role))
        else:
            await message.reply(
                "Для доступа к этому разделу необходима подписка уровня SUPER_USER.",
                reply_markup=KeyBoards.get_keyboard(role)
            )

    @dp.message_handler(text='Список дней рождений')
    @staticmethod
    async def birthdays_list(message: types.Message):
        role = getattr(message, 'role', 'user')
        logger.info(f"Пользователь {message.from_user.id} (роль {role}) запросил список дней рождений.")
        RecordLogs.log_user_action(message.from_user.id, "запросил список дней рождений.")
        try:
            await get_all_birthdays(message)
        except Exception as e:
            #await message.reply(f"Произошла ошибка: {e}", reply_markup=KeyBoards.get_keyboard(role))
            logger.error(f"У пользователя {message.from_user.id} произошла ошибка: {e}")
            RecordLogs.log_user_action(message.from_user.id, f"произошла ошибка: {e}")


    @dp.message_handler(text='Список пользователей')
    @staticmethod
    async def users_list(message: types.Message):
        role = getattr(message, 'role', 'user')
        if role != 'admin':
            await message.reply("У вас нет доступа к этому разделу.", reply_markup=KeyBoards.get_keyboard(role))
            logger.warning(f"Пользователь {message.from_user.id} попытался получить доступ к списку пользователей.")
            RecordLogs.log_user_action(message.from_user.id, "попытался получить доступ к списку пользователей.")
            return
        logger.info(f"Администратор {message.from_user.id} запросил список пользователей.")
        RecordLogs.log_admin_action(message.from_user.id, "запросил список пользователей.")
        try:
            await get_all_users(message)
            #users = read_csv_data('users.csv', 'users')
            #if users:
            #    await message.reply("Список пользователей:\n" + "\n".join(users), reply_markup=KeyBoards.get_keyboard(role))
            #else:
            #await message.reply("В списке нет пользователей.", reply_markup=KeyBoards.get_keyboard(role))
        except FileNotFoundError:
            await message.reply("Файл users.csv не найден.", reply_markup=KeyBoards.get_keyboard(role))
            logger.error("Файл users.csv не найден.")
        except Exception as e:
            await message.reply(f"Произошла ошибка: {e}", reply_markup=KeyBoards.get_keyboard(role))
            logger.error(f"У администратора {message.from_user.id} произошла ошибка: {e}")
            RecordLogs.log_admin_action(message.from_user.id, "произошла ошибка")