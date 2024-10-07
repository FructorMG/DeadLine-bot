from aiogram.types import ReplyKeyboardMarkup

class KeyBoards:
    # Основная клавиатура
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Список дней рождений', 'Добавить день рождения', 'Помощь')

    # Клавиатура администратора
    admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    admin_keyboard.add('Список дней рождений', 'Добавить день рождения', 'Список пользователей')

    @classmethod
    def get_keyboard(cls, role: str) -> ReplyKeyboardMarkup:
        if role == 'admin':
            return cls.admin_keyboard
        else:
            return cls.keyboard

