import csv
from datetime import datetime
import asyncio
from aiogram import Bot
from config import BOT_TOKEN, CHAT_ID
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Инициализация бота
bot = Bot(token=BOT_TOKEN)

async def check_deadlines():
    today = datetime.now().strftime("%d.%m")
    birthdays_today = []
    logging.info(f"Проверка дедлайнов на дату: {today}")

    try:
        with open('birthdays.csv', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                fio = row.get('fio')
                bdate = row.get('bdate')
                if bdate == today:
                    birthdays_today.append(fio)
    except FileNotFoundError:
        logging.error("Файл birthdays.csv не найден.")
        await bot.send_message(CHAT_ID, "❌ Файл birthdays.csv не найден.")
        return
    except Exception as e:
        logging.error(f"Ошибка при чтении файла: {e}")
        await bot.send_message(CHAT_ID, f"❌ Произошла ошибка при чтении файла: {e}")
        return

    if birthdays_today:
        for fio in birthdays_today:
            message = f"🎉 Сегодня день рождения у {fio}! 🎂"
            await bot.send_message(CHAT_ID, message)
            logging.info(f"Отправлено сообщение о дне рождения: {fio}")
    else:
        logging.info("Сегодня нет дней рождения.")

async def send_start_message():
    await bot.send_message(CHAT_ID, "🤖 Бот запущен и работает!")
    logging.info("Отправлено стартовое сообщение.")

async def main():
    await send_start_message()
    while True:
        await check_deadlines()
        # Ждём до следующего дня (24 часа)
        await asyncio.sleep(24 * 60 * 60)

if __name__ == "__main__":
    asyncio.run(main())
