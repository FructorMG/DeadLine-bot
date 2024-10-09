import logging
from aiogram import types
from bot.bot import dp
from bot.bd import get_all_users, get_all_birthdays, Sup_get_all_birthdays
from bot.Keyboards import KeyBoards
from bot.config import config
from bot.Utils.Record_Logs import RecordLogs
from bot.Handlers.user_registration import UserRegistration
from bot.Handlers.super_user_registration import SuperUserRegistration

logger = logging.getLogger("bot.handler")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

def setup_handlers():
    UserRegistration()
    SuperUserRegistration()
class Handlers:
    @dp.message_handler(text = "Помощь")
    @staticmethod
    async def support(message: types.Message, role: str = "user"):
        assistants = ", ".join([str(id_) for id_ in config.assistants_list])
        await message.reply(f"Если вы заметили ошибку или хотите поделиться своими пожеланиями по поводу бота, пожалуйста, свяжитесь с {assistants}.",
                            reply_markup = KeyBoards.get_keyboard(role)
        )
        logger.info(f"Пользователь {message.from_user.id} запросил помощь.")

    #@dp.message_handler(text = "Добавить день рождения")
    #@staticmethod
    #async def add_birthday(message: types.Message, role: str):
    #    if role == "super_users":
    #        await message.reply("Функция добавления дня рождения пока не реализована.", reply_markup = KeyBoards.get_keyboard(role))
    #        logger.info(f"Суперпользователь {message.from_user.id} попытался добавить день рождения.")
    #    else:
    #        await message.reply("Для доступа к этому разделу необходима подписка уровня SUPER_USER.", reply_markup = KeyBoards.get_keyboard(role))
    #        logger.warning(f"Пользователь {message.from_user.id} без прав пытался добавить день рождения.")

    @dp.message_handler(text = "Список дней рождений")
    @staticmethod
    async def birthdays_list(message: types.Message, role: str):
        logger.info(f"Пользователь {message.from_user.id} (роль {role}) запросил список дней рождений.")
        RecordLogs.log_user_action(message.from_user.id, "запросил список дней рождений.")
        try:
            if role == "super_user":
                await get_all_birthdays(message)
                await Sup_get_all_birthdays(message)
            else:
                await get_all_birthdays(message)
        except Exception as e:
            await message.reply(f"Произошла ошибка: {e}", reply_markup = KeyBoards.get_keyboard(role))
            logger.error(f"У пользователя {message.from_user.id} произошла ошибка: {e}")
            RecordLogs.log_user_action(message.from_user.id, f"произошла ошибка: {e}")

    @dp.message_handler(text = "Список пользователей")
    @staticmethod
    async def users_list(message: types.Message, role: str):
        if role != "admin":
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
    # @dp.message_handler(command = ['/block'])
    # @staticmethod
    # async def user_block(message: types.Message, role: str):
    #     if role != 'admin':
    #         await message.reply("У вас нет доступа к этой команде.", reply_markup = KeyBoards.get_keyboard(role))
