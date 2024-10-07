import asyncio
from aiogram import types
from datetime import datetime, timedelta
import logging
from bot.Utils.csv_utils import read_csv_data
from bot.bot import bot
from bot.bd import session, User
from bot.Utils.Record_Logs import RecordLogs

logger = logging.getLogger("bot")

async def check_deadlines():
    today = datetime.now().strftime("%d.%m")
    logger.info(f"Проверка дней рождения на дату: {today}")
    try:
        birthdays = read_csv_data('birthdays.csv', 'birthdays')
        for entry in birthdays:
            try:
                fio, bdate = entry.split(': ')
                if bdate == today:
                    users = session.query(User).all()  # Получаем всех пользователей
                    if users:
                        message = f"🎉 Сегодня день рождения у {fio}!"
                        for user in users:  # Перебираем всех пользователей и отправляем сообщение
                            await bot.send_message(user.user_id, text=message)
                            logger.info(f"Отправлено сообщение пользователю {user.user_id}: {message}")
                    else:
                        logger.warning(f"Нет пользователей в базе данных.")
            except ValueError:
                logger.warning(f"Некорректный формат записи: {entry}")
                RecordLogs.error_log(user.user_id, 'Некорректный формат записи')
    except FileNotFoundError:
        logger.error("Файл birthdays.csv не найден.")
        RecordLogs.error_log(user.user_id,'Файл birthdays.csv не найден.')
    except Exception as e:
        logger.error(f"Произошла ошибка при проверке дедлайнов: {e}")
        RecordLogs.error_log(user.user_id, 'Произошла ошибка при проверке дедлайнов')

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
