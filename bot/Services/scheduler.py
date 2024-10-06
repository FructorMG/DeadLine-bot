# bot/Services/scheduler.py

import asyncio
from datetime import datetime, timedelta
import logging
from bot.Utils.csv_utils import read_csv_data
from bot.bot import bot
from bot.config import config

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
                    message = f"🎉 Сегодня день рождения у {fio}!"
                    await bot.send_message(config.CHAT_ID, text=message)
                    logger.info(f"Отправлено сообщение: {message}")
            except ValueError:
                logger.warning(f"Некорректный формат записи: {entry}")
    except FileNotFoundError:
        logger.error("Файл birthdays.csv не найден.")
    except Exception as e:
        logger.error(f"Произошла ошибка при проверке дедлайнов: {e}")

async def scheduled_check():
    logger.info("Бот запущен и начал проверку дедлайнов.")
    try:
        await bot.send_message(config.CHAT_ID, text="🚀 Бот запущен и начал проверку дедлайнов!")
    except Exception as e:
        logger.error(f"Не удалось отправить стартовое сообщение: {e}")
    while True:
        await check_deadlines()
        now = datetime.now()
        next_run = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        sleep_duration = (next_run - now).total_seconds()
        hours = sleep_duration // 3600
        minutes = (sleep_duration % 3600) // 60
        logger.info(f"Следующая проверка через {int(hours)} часа(ов) и {int(minutes)} минут.")
        await asyncio.sleep(sleep_duration)
