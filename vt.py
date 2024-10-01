import csv
from datetime import datetime
import asyncio
from aiogram import Bot
from config import BOT_TOKEN, CHAT_ID
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BirthdayManager:
    def __init__(self, csv_file='birthdays.csv'):
        self.csv_file = csv_file

    def get_today_birthdays(self):
        """Возвращает список имен, у которых сегодня день рождения."""
        today = datetime.now().strftime("%d.%m")
        birthdays_today = []
        logging.info(f"Проверка дней рождения на дату: {today}")
        try:
            with open(self.csv_file, encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    fio = row.get('fio')
                    bdate = row.get('bdate')
                    if bdate == today:
                        birthdays_today.append(fio)
        except FileNotFoundError:
            logging.error(f"Файл {self.csv_file} не найден.")
            raise
        except Exception as e:
            logging.error(f"Ошибка при чтении файла {self.csv_file}: {e}")
            raise
        return birthdays_today
class TelegramBot:
    def __init__(self, token, chat_id, birthday_manager):
        self.bot = Bot(token=token)
        self.chat_id = chat_id
        self.birthday_manager = birthday_manager

    async def send_message(self, message):
        try:
            await self.bot.send_message(self.chat_id, message)
            logging.info(f"Отправлено сообщение: {message}")
        except Exception as e:
            logging.error(f"Не удалось отправить сообщение: {e}")

    async def send_start_message(self):
        """Отправляет стартовое сообщение при запуске бота."""
        message = "🤖 Бот запущен и работает!"
        await self.send_message(message)
        logging.info("Отправлено стартовое сообщение.")

    async def notify_birthdays(self):
        """Проверяет и уведомляет о днях рождения."""
        try:
            birthdays_today = self.birthday_manager.get_today_birthdays()
        except FileNotFoundError:
            await self.send_message("❌ Файл birthdays.csv не найден.")
            return
        except Exception as e:
            await self.send_message(f"❌ Произошла ошибка при чтении файла: {e}")
            return

        if birthdays_today:
            for fio in birthdays_today:
                message = f"🎉 Сегодня день рождения у {fio}! 🎂"
                await self.send_message(message)
        else:
            logging.info("Сегодня нет дней рождения.")

    async def run(self):
        """Основной цикл работы бота."""
        await self.send_start_message()
        while True:
            await self.notify_birthdays()
            await asyncio.sleep(24 * 60 * 60)  # Ждет 24 часа

async def main():
    birthday_manager = BirthdayManager()
    telegram_bot = TelegramBot(token=BOT_TOKEN, chat_id=CHAT_ID, birthday_manager=birthday_manager)
    await telegram_bot.run()


if __name__ == "__main__":
    asyncio.run(main())
