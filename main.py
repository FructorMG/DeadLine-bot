import csv
import asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message
import config

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot=bot)

class RoleMiddleware(BaseMiddleware):
    def __init__(self):
        super(RoleMiddleware, self).__init__()

    async def on_process_message(self, message: Message, data: dict):
        user_id = message.from_user.id
        if str(user_id) in config.ADMINS:
            data['role'] = 'admin'
        elif str(user_id) in config.ASSISTANTS:
            data['role'] = 'assistant'
        elif str(user_id) in config.SUPER_USERS:
           data['role'] = 'super_users'
        else:
            data['role'] = 'user'
dp.middleware.setup(RoleMiddleware())


keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add('Список дней рождений').add('Добавить день рождения').add('Помощь')

admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
admin_keyboard.add('Список дней рождений').add('Добавить день рождения').add('Список пользователей')

def keyboard_check(message: types.Message):
    if config.ADMINS and message.from_user.id == config.ADMINS:
        return admin_keyboard
    else:
        return keyboard

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    config.logger.info(f"Пользователь {message.from_user.id} вызвал команду /start.")
    await message.reply("Привет! Я бот для уведомлений о днях рождения.", reply_markup = keyboard_check(message))

@dp.message_handler(text='Помощь')
async def support(message: types.Message):
    await message.reply(f'Если вы заметили ошибку или хотите поделиться своими пожеланиями по поводу бота, пожалуйста, свяжитесь с {config.ASSISTANTS}.\n', reply_markup = keyboard_check(message))

@dp.message_handler(text='Добавить день рождения')
async def add_birthday(message: types.Message, role: str):
    # РЕАЛИЗОВАТЬ
    if role == 'super_users' :
        await message.reply("Реализовать.", reply_markup = keyboard_check(message))
    else:
        await message.reply("Для доступа к этому разделу необходима подписка уровня SUPER_USER.", reply_markup=keyboard_check(message))

def read_csv_data(file_path, data_type):
    result = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) < 2:
                config.logger.warning(f"Некорректная строка в CSV: {row}")
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
    config.logger.info(f"Администратор {message.from_user.id} запросил список дней рождений.")
    try:
        with open('birthdays.csv', mode='r', encoding='utf-8') as file:
            birthdays = read_csv_data('birthdays.csv', 'birthdays')
        if birthdays:
            await message.reply("Список дней рождений:\n" + "\n".join(birthdays), reply_markup = keyboard_check(message))
        else:
            await message.reply("В списке нет дней рождений.", reply_markup = keyboard_check(message))
    except FileNotFoundError:
        await message.reply("Файл birthdays.csv не найден.", reply_markup = keyboard_check(message))
        config.logger.error("Файл birthdays.csv не найден.")
    except Exception as e:
        await message.reply(f"Произошла ошибка: {e}", reply_markup = keyboard_check(message))
        config.logger.error(f"У пользователя {message.from_user.id} произошла ошибка: {e}")

@dp.message_handler(text='Список пользователей')
async def users_list(message: types.Message, role: str):
    if role != 'admin':
        await message.reply("У вас нет доступа к этому разделу.", reply_markup = keyboard_check(message))
        config.logger.warning(f"Пользователь {message.from_user.id} попытался получить доступ к списку пользователей.")
        #f = open('logs.txt', 'a'); f.write(f"WARNING|Пользователь {message.from_user.id} попытался получить доступ к списку пользователей.\n"); f.close()
        return
    #f = open('logs.txt', 'a'); f.write(f"Администратор {message.from_user.id} запросил список пользователей.\n");f.close()
    config.logger.info(f"Администратор {message.from_user.id} запросил список пользователей.")
    try:
        users = read_csv_data('users.csv', 'users')
        if users:
            await message.reply("Список пользователей:\n" + "\n".join(users), reply_markup = keyboard_check(message))
        else:
            await message.reply("В списке нет пользователей.", reply_markup = keyboard_check(message))
    except FileNotFoundError:
        await message.reply("Файл users.csv не найден.", reply_markup = keyboard_check(message))
        config.logger.error("Файл users.csv не найден.")
    except Exception as e:
        await message.reply(f"Произошла ошибка: {e}", reply_markup = keyboard_check(message))
        config.logger.error(f"У администратора {message.from_user.id} произошла ошибка: {e}")
        #f = open('logs.txt', 'a'); f.write(f"У администратора {message.from_user.id} произошла ошибка: {e}\n"); f.close()

async def check_deadlines():
    today = datetime.now().strftime("%d.%m")
    config.logger.info(f"Проверка дней рождения на дату: {today}")
    try:
        birthdays = read_csv_data('birthdays.csv', 'birthdays')
        for entry in birthdays:
            try:
                fio, bdate = entry.split(': ')
                if bdate == today:
                    message = f"🎉 Сегодня день рождения у {fio}!"
                    await bot.send_message(config.CHAT_ID, text=message)
                    config.logger.info(f"Отправлено сообщение: {message}")
            except ValueError:
                config.logger.warning(f"Некорректный формат записи: {entry}")
    except FileNotFoundError:
        config.logger.error("Файл birthdays.csv не найден.\n")
    except Exception as e:
        config.logger.error(f"Произошла ошибка при проверке дедлайнов: {e}\n")


async def scheduled_check():
    config.logger.info("Бот запущен и начал проверку дедлайнов.")
    #f = open('logs.txt', 'a'); f.write("Бот запущен и начал проверку дедлайнов.\n"); f.close()
    await bot.send_message(config.CHAT_ID, text="🚀 Бот запущен и начал проверку дедлайнов!")
    while True:
        await check_deadlines()
        now = datetime.now()
        next_run = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        sleep_duration = (next_run - now).total_seconds()
        hours = sleep_duration // 3600
        minutes = (sleep_duration % 3600) // 60
        config.logger.info(f"Следующая проверка через {int(hours)} часа(ов) и {int(minutes)} минут.\n")
        await asyncio.sleep(sleep_duration)

async def on_startup(dispatcher):
    config.logger.info("Выполнение on_startup.")
    asyncio.create_task(scheduled_check())

if __name__ == '__main__':
    config.logger.info("Запуск бота.")
    executor.start_polling(dp, on_startup=on_startup)