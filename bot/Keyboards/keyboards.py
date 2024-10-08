from aiogram.types import ReplyKeyboardMarkup

class KeyBoards:
    # Основная клавиатура
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Список дней рождений').add('Добавить день рождения'.add('Помощь')

    # Клавиатура администратора
    admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    admin_keyboard.add('Список дней рождений').add('Добавить день рождения').add('Список пользователей')

    #Клавиатура для регистрации
    registration_keyboard = ReplyKeyboardMarkup(resize_keyboard = True)
    registration_keyboard.add('Да').add('Нет')

    @classmethod
    def get_keyboard(cls, role: str) -> ReplyKeyboardMarkup:
        if role == 'admin':
            return cls.admin_keyboard
        else:
            return cls.keyboard

