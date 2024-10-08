import asyncio
from aiogram import types
from datetime import datetime, timedelta
import logging
from bot.Utils.csv_utils import read_csv_data
from bot.bot import bot
from bot.bd import session, User
from bot.Utils.Record_Logs import RecordLogs

logger = logging.getLogger("bot")

from datetime import datetime


async def check_deadlines():
    today = datetime.now().strftime("%d.%m")  # Получаем текущую дату в формате "день.месяц"
    logger.info(f"Проверка дней рождения на дату: {today}")
    try:
        today_date = datetime.now().date()
        birthday_date_str = today_date.strftime("%Y-%m-%d")

        users_with_birthdays = session.query(User).filter(User.birthday_date == birthday_date_str).all()
        if users_with_birthdays:
            for user in users_with_birthdays:
                message = f"🎉 Сегодня день рождения у {user.name}!"
                users = session.query(User).all()
                for recipient in users:
                    await bot.send_message(recipient.user_id, text=message)
                    logger.info(f"Отправлено сообщение пользователю {recipient.user_id}: {message}")
        else:
            logger.info("Сегодня нет пользователей с днями рождения.")
    except Exception as e:
        logger.error(f"Произошла ошибка при проверке дней рождения: {e}")
        RecordLogs.error_log(None, f'Произошла ошибка при проверке дней рождения: {e}')


async def scheduled_check():
    logger.info("Бот запущен и начал проверку дедлайнов.")
    try:
        users = session.query(User).all()
        for user in users:
            try:
                await bot.send_message(user.user_id, text="🚀 Бот запущен и начал проверку дедлайнов!")
            except Exception as e:
                logger.error(f"Не удалось отправить стартовое сообщение пользователю {user.user_id}: {e}")
                RecordLogs.error_log(user.user_id, 'Не удалось отправить стартовое сообщение пользователю ')
    except Exception as e:
        logger.error(f"Ошибка при отправке стартовых сообщений: {e}")
        RecordLogs.error_log(user.user_id, 'Ошибка при отправке стартовых сообщений')

    while True:
        await check_deadlines()
        now = datetime.now()
        next_run = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        sleep_duration = (next_run - now).total_seconds()
        hours = sleep_duration // 3600
        minutes = (sleep_duration % 3600) // 60
        logger.info(f"Следующая проверка через {int(hours)} часа(ов) и {int(minutes)} минут.")
        await asyncio.sleep(sleep_duration)