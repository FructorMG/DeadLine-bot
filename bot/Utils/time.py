from datetime import datetime
from aiogram import types

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open('logs.txt', 'a') as f:
    f.write(f"{current_time} - Администратор {message.from_user.id} запросил список пользователей.\n")
