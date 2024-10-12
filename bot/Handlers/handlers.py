import logging
from aiogram import types
from bot.bot import dp
from bot.bd import get_all_users, get_all_birthdays, Sup_get_all_birthdays, get_ban_list
from bot.Keyboards import KeyBoards
from bot.config import config
from bot.Utils.Record_Logs import RecordLogs
from bot.Middleware.secure_middleware import rate_limit
logger = logging.getLogger("bot.handler")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)



class Handlers:
    @dp.message_handler(text="Помощь")
    @rate_limit(5, 'support')
    @staticmethod
    async def support(message: types.Message, role: str = "user"):
        assistants = ", ".join([str(id_) for id_ in config.assistants_list])
        await message.reply(
            f"Если вы заметили ошибку или хотите поделиться своими пожеланиями по поводу бота, пожалуйста, свяжитесь с {assistants}.",
            reply_markup=KeyBoards.get_keyboard(role)
            )
        logger.info(f"Пользователь {message.from_user.id} запросил помощь.")

    @rate_limit(3, 'birthdays_list')
    @dp.message_handler(text="Список дней рождений")
    @staticmethod
    async def birthdays_list(message: types.Message, role: str):
        logger.info(f"Пользователь {message.from_user.id} (роль {role}) запросил список дней рождений.")
        RecordLogs.log_user_action(message.from_user.id, "запросил список дней рождений.")
        try:
            if role == "super_users" or "admin":
                # await message.reply(f"2")
                await get_all_birthdays(message)
                await Sup_get_all_birthdays(message)
            else:
                # await message.reply(f"1")
                await get_all_birthdays(message)
        except Exception as e:
            await message.reply(f"Произошла ошибка: {e}", reply_markup=KeyBoards.get_keyboard(role))
            logger.error(f"У пользователя {message.from_user.id} произошла ошибка: {e}")
            RecordLogs.log_user_action(message.from_user.id, f"произошла ошибка: {e}")

    @rate_limit(3, 'users_list')
    @dp.message_handler(text="Список пользователей")
    @staticmethod
    async def users_list(message: types.Message, role: str):
        if role != "admin":
            await message.reply("У вас нет доступа к этому разделу.", reply_markup=KeyBoards.get_keyboard(role))
            logger.warning(f"Пользователь {message.from_user.id} попытался получить доступ к списку пользователей.")
            RecordLogs.log_user_action(message.from_user.id, "попытался получить доступ к списку пользователей.")
            return
        logger.info(f"Администратор {message.from_user.id} запросил список пользователей.")
        RecordLogs.log_admin_action(message.from_user.id, "запросил список пользователей.")
        await get_all_users(message)


    @rate_limit(3, 'Ban')
    @dp.message_handler(text="Ban")
    async def admin_ban(message: types.Message, role: str):
        if role != 'admin':
            await message.reply("У вас нет доступа к этому разделу.", reply_markup=KeyBoards.get_keyboard(role))
            logger.warning(f"Пользователь {message.from_user.id} попытался получить доступ к бан листу.")
            RecordLogs.log_user_action(message.from_user.id, "попытался получить доступ к списку пользователей.")
        else:
            await message.reply("Выберите опцию", reply_markup = KeyBoards.admin_ban_keyboard)
            logger.info(f"Администратор {message.from_user.id} зашел в бан лист.")
            RecordLogs.log_admin_action(message.from_user.id, "зашел в бан лист.")

    @rate_limit(3, 'ban_list')
    @dp.message_handler(text="Список забаненых пользователей")
    async def admin_ban(message: types.Message, role: str):
        if role != 'admin':
            await message.reply("У вас нет доступа к этому разделу.", reply_markup=KeyBoards.get_keyboard(role))
            logger.warning(f"Пользователь {message.from_user.id} попытался получить доступ к бан листу.")
            RecordLogs.log_user_action(message.from_user.id, "попытался получить доступ к списку пользователей.")
        else:
            await get_ban_list(message)
            logger.info(f"Администратор {message.from_user.id} зашел в бан лист.")
            RecordLogs.log_admin_action(message.from_user.id, "зашел в бан лист.")

    @rate_limit(3, 'Return')
    @dp.message_handler(text="Вернуться в меню")
    async def admin_ban(message: types.Message, role: str):
        await message.reply("Возврат в меню", reply_markup=KeyBoards.get_keyboard(role))



