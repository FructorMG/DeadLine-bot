import os
import csv
import asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
SUPPORT_ID = os.getenv('SUPPORT_ID')
ADMIN_ID = os.getenv('ADMIN_ID')

if not BOT_TOKEN:
    logger.error("Не найден BOT_TOKEN в переменных окружения.")
    raise ValueError("Не найден BOT_TOKEN в переменных окружения.")
if not CHAT_ID:
    logger.error("Не найден CHAT_ID в переменных окружения.")
    raise ValueError("Не найден CHAT_ID в переменных окружения.")
if not SUPPORT_ID:
    logger.info("СИСТЕМА: ОТСУТСВУЕТ SUPPORT_ID в переменных окружения ")
if not ADMIN_ID:
    logger.info("СИСТЕМА: ОТСУТСВУЕТ ADMIN_ID в переменных окружения ")
try:
    ADMIN_ID = int(ADMIN_ID)
except (TypeError, ValueError):
    ADMIN_ID = None
    logger.warning("ADMIN_ID не установлен или некорректен.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot=bot)

keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add('Список дней рождений').add('Добавить день рождения').add('Помощь')

admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
admin_keyboard.add('Список дней рождений').add('Добавить день рождения').add('Список пользователей')

def keyboard_check(message: types.Message):
    if ADMIN_ID and message.from_user.id == ADMIN_ID:
        return admin_keyboard
    else:
        return keyboard

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} вызвал команду /start.")
    await message.reply("Привет! Я бот для уведомлений о днях рождения.", reply_markup = keyboard_check(message))

@dp.message_handler(text='Помощь')
async def support(message: types.Message):
    await message.reply(f'Если вы заметили ошибку или хотите поделиться своими пожеланиями по поводу бота, пожалуйста, свяжитесь с {SUPPORT_ID}.\n',reply_markup = keyboard_check(message))

@dp.message_handler(text='Добавить день рождения')
async def add_birthday(message: types.Message):
    # РЕАЛИЗОВАТЬ
    await message.reply("Реализовать.", reply_markup = keyboard_check(message))

def read_csv_data(file_path, data_type):
    result = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) < 2:
                logger.warning(f"Некорректная строка в CSV: {row}")
                continue
            fio = row[0].strip()
            if data_type == 'users':
                username = row[1].strip()
                result.append(f"{fio}: @{username}")
            elif data_type == 'birthdays':
                bdate = row[1].strip()
                result.append(f"{fio}: {bdate}")

    return result

@dp.message_handler(text='Список дней рождений')
async def birthdays_list(message: types.Message):
    logger.info(f"Администратор {message.from_user.id} запросил список дней рождений.")
    try:
        with open('birthdays.csv', mode='r', encoding='utf-8') as file:
            birthdays = read_csv_data('birthdays.csv', 'birthdays')
        if birthdays:
            await message.reply("Список дней рождений:\n" + "\n".join(birthdays), reply_markup = keyboard_check(message))
        else:
            await message.reply("В списке нет дней рождений.", reply_markup = keyboard_check(message))
    except FileNotFoundError:
        await message.reply("Файл birthdays.csv не найден.", reply_markup = keyboard_check(message))
        logger.error("Файл birthdays.csv не найден.")
    except Exception as e:
        await message.reply(f"Произошла ошибка: {e}", reply_markup = keyboard_check(message))
        logger.error(f"У пользователя {message.from_user.id} произошла ошибка: {e}")

@dp.message_handler(text='Список пользователей')
async def users_list(message: types.Message):
    if ADMIN_ID and message.from_user.id != ADMIN_ID:
        await message.reply("У вас нет доступа к этому разделу.", reply_markup = keyboard_check(message))
        logger.warning(f"Пользователь {message.from_user.id} попытался получить доступ к списку пользователей.")
        f = open('logs.txt', 'a'); f.write(f"WARNING|Пользователь {message.from_user.id} попытался получить доступ к списку пользователей.\n"); f.close()
        return
    f = open('logs.txt', 'a'); f.write(f"Администратор {message.from_user.id} запросил список пользователей.\n");f.close()
    logger.info(f"Администратор {message.from_user.id} запросил список пользователей.")
    try:
        users = read_csv_data('users.csv', 'users')
        if users:
            await message.reply("Список пользователей:\n" + "\n".join(users), reply_markup = keyboard_check(message))
        else:
            await message.reply("В списке нет пользователей.", reply_markup = keyboard_check(message))
    except FileNotFoundError:
        await message.reply("Файл users.csv не найден.", reply_markup = keyboard_check(message))
        logger.error("Файл users.csv не найден.")
    except Exception as e:
        await message.reply(f"Произошла ошибка: {e}", reply_markup = keyboard_check(message))
        logger.error(f"У администратора {message.from_user.id} произошла ошибка: {e}")
        f = open('logs.txt', 'a'); f.write(f"У администратора {message.from_user.id} произошла ошибка: {e}\n"); f.close()

async def check_deadlines():
    today = datetime.now().strftime("%d.%m")
    logger.info(f"Проверка дней рождения на дату: {today}")
    try:
        with open('birthdays.csv', mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) < 2:
                    logger.warning(f"Некорректная строка в CSV: {row}")
                    continue
                fio, bdate = row[0].strip(), row[1].strip()
                if bdate == today:
                    message = f"🎉 Сегодня день рождения у {fio}!"
                    await bot.send_message(CHAT_ID, text=message)
                    logger.info(f"Отправлено сообщение: {message}")
    except FileNotFoundError:
        logger.error("Файл birthdays.csv не найден.\n")
        f = open('logs.txt', 'a'); f.write("Файл birthdays.csv не найден.\n"); f.close()
    except Exception as e:
        logger.error(f"Произошла ошибка при проверке дедлайнов: {e}\n")
        f = open('logs.txt', 'a'); f.write(f"Произошла ошибка при проверке дедлайнов: {e}\n"); f.close()

async def scheduled_check():
    logger.info("Бот запущен и начал проверку дедлайнов.")
    f = open('logs.txt', 'a'); f.write("Бот запущен и начал проверку дедлайнов.\n"); f.close()
    await bot.send_message(CHAT_ID, text="🚀 Бот запущен и начал проверку дедлайнов!")
    while True:
        await check_deadlines()
        now = datetime.now()
        next_run = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        sleep_duration = (next_run - now).total_seconds()
        hours = sleep_duration // 3600
        minutes = (sleep_duration % 3600) // 60
        logger.info(f"Следующая проверка через {int(hours)} часа(ов) и {int(minutes)} минут.\n")
        await asyncio.sleep(sleep_duration)

async def on_startup(dispatcher):
    logger.info("Выполнение on_startup.")
    asyncio.create_task(scheduled_check())

if __name__ == '__main__':
    logger.info("Запуск бота.")
    executor.start_polling(dp, on_startup=on_startup)
