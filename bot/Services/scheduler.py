import logging
import asyncio
from datetime import timedelta
import logging
from bot.bot import bot
from bot.bd import session, User, SuperUser
from bot.Utils.Record_Logs import RecordLogs
from sqlalchemy import extract
from datetime import datetime


logger = logging.getLogger("bot")

async def check_deadlines():
    today = datetime.now()
    logger.info(f"Проверка дней рождения на дату: {today.strftime('%d.%m')}")
    try:
        current_month = today.month
        current_day = today.day
        users_with_birthdays = session.query(User).filter(
            extract('month', User.birthday_date) == current_month,
            extract('day', User.birthday_date) == current_day
        ).all()

        if users_with_birthdays:
            recipient_users = session.query(User.user_id).distinct().all()
            recipient_user_ids = {user_id for (user_id,) in recipient_users}

            for user in users_with_birthdays:
                message = f"🎉 Сегодня день рождения у {user.name}!"
                for recipient_id in recipient_user_ids:
                    await bot.send_message(recipient_id, text=message)
                    logger.info(f"Отправлено сообщение пользователю {recipient_id}: {message}")
        else:
            logger.info("Сегодня нет пользователей с днями рождения.")

        superusers_with_birthdays = session.query(SuperUser).filter(
            extract('month', SuperUser.birthday_date) == current_month,
            extract('day', SuperUser.birthday_date) == current_day
        ).all()

        if superusers_with_birthdays:
            recipient_superusers = session.query(SuperUser.super_user_id).distinct().all()
            recipient_superuser_ids = {su_id for (su_id,) in recipient_superusers}

            for superuser in superusers_with_birthdays:
                message = f"🎉 Сегодня день рождения у вашего пользователя {superuser.name}!"
                for recipient_id in recipient_superuser_ids:
                    await bot.send_message(recipient_id, text=message)
                    logger.info(f"Отправлено сообщение суперпользователю {recipient_id}: {message}")
        else:
            logger.info("Сегодня нет ваших пользователей с днями рождения.")

    except Exception as e:
        logger.error(f"Произошла ошибка при проверке дней рождения: {e}")
        RecordLogs.error_log(None, f"Произошла ошибка при проверке дней рождения: {e}")

async def scheduled_check():
    logger.info("Бот запущен и начал проверку дедлайнов.")
    try:
        users = session.query(User).all()
        for user in users:
            try:
                print("1")
                #await bot.send_message(user.user_id, text="🚀 Бот запущен и начал проверку дедлайнов!")
            except Exception as e:
                logger.error(f"Не удалось отправить стартовое сообщение пользователю {User.user_id}: {e}")
                RecordLogs.error_log(user.user_id, "Не удалось отправить стартовое сообщение пользователю ")
    except Exception as e:
        logger.error(f"Ошибка при отправке стартовых сообщений: {e}")
        RecordLogs.error_log(User.user_id, "Ошибка при отправке стартовых сообщений")

    while True:
        await check_deadlines()
        now = datetime.now()
        next_run = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        sleep_duration = (next_run - now).total_seconds()
        hours = sleep_duration // 3600
        minutes = (sleep_duration % 3600) // 60
        logger.info(f"Следующая проверка через {int(hours)} часа(ов) и {int(minutes)} минут.")
        await asyncio.sleep(sleep_duration)