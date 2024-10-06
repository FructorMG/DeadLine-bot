import logging
from aiogram import types
from bot.bot import dp
from bot.Keyboards import KeyBoards
from bot.Utils.csv_utils import read_csv_data
from bot.Utils.Record_Logs import RecordLogs
from bot.config import config

logger = logging.getLogger("bot")

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    role = getattr(message, 'role', 'user')
    logger.info(f"Пользователь {message.from_user.id} вызвал команду /start.")
    await message.reply("Привет! Я бот для уведомлений о днях рождения.", reply_markup=KeyBoards.get_keyboard(role))

@dp.message_handler(text='Помощь')
async def support(message: types.Message):
    role = getattr(message, 'role', 'user')
    assistants = ", ".join([str(id_) for id_ in config.assistants_list])
    await message.reply(
        f'Если вы заметили ошибку или хотите поделиться своими пожеланиями по поводу бота, пожалуйста, свяжитесь с {assistants}.',
        reply_markup=KeyBoards.get_keyboard(role)
    )

@dp.message_handler(text='Добавить день рождения')
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
async def birthdays_list(message: types.Message):
    role = getattr(message, 'role', 'user')
    logger.info(f"Пользователь {message.from_user.id} (роль {role}) запросил список дней рождений.")
    RecordLogs.log_user_action(message.from_user.id, "запросил список дней рождений.")

    try:
        birthdays = read_csv_data('birthdays.csv', 'birthdays')
        if birthdays:
            await message.reply("Список дней рождений:\n" + "\n".join(birthdays), reply_markup=KeyBoards.get_keyboard(role))
        else:
            await message.reply("В списке нет дней рождений.", reply_markup=KeyBoards.get_keyboard(role))
    except FileNotFoundError:
        await message.reply("Файл birthdays.csv не найден.", reply_markup=KeyBoards.get_keyboard(role))
        logger.error("Файл birthdays.csv не найден.")
    except Exception as e:
        await message.reply(f"Произошла ошибка: {e}", reply_markup=KeyBoards.get_keyboard(role))
        logger.error(f"У пользователя {message.from_user.id} произошла ошибка: {e}")
        RecordLogs.log_user_action(message.from_user.id, "произошла ошибка")

@dp.message_handler(text='Список пользователей')
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
        users = read_csv_data('users.csv', 'users')
        if users:
            await message.reply("Список пользователей:\n" + "\n".join(users), reply_markup=KeyBoards.get_keyboard(role))
        else:
            await message.reply("В списке нет пользователей.", reply_markup=KeyBoards.get_keyboard(role))
    except FileNotFoundError:
        await message.reply("Файл users.csv не найден.", reply_markup=KeyBoards.get_keyboard(role))
        logger.error("Файл users.csv не найден.")
    except Exception as e:
        await message.reply(f"Произошла ошибка: {e}", reply_markup=KeyBoards.get_keyboard(role))
        logger.error(f"У администратора {message.from_user.id} произошла ошибка: {e}")
        RecordLogs.log_admin_action(message.from_user.id, "произошла ошибка")