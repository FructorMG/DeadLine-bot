from aiogram.types import ReplyKeyboardMarkup

class KeyBoards:
    # Основная клавиатура
    keyboard = ReplyKeyboardMarkup(resize_keyboard = True)
    keyboard.add("Список дней рождений").add("Добавить день рождения").add("Помощь")

    # Клавиатура администратора
    admin_keyboard = ReplyKeyboardMarkup(resize_keyboard = True)
    admin_keyboard.add("Список дней рождений").add("Добавить день рождения").add("Список пользователей").add("Ban")

    admin_ban_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    admin_ban_keyboard.add("Список забаненых пользователей").add("Забанить пользователя").add("Вернуться в меню")

    #Клавиатура для регистрации
    registration_keyboard = ReplyKeyboardMarkup(resize_keyboard = True)
    registration_keyboard.add("Да").add("Нет")

    #Клавиатура для отмены регистрации в user_registraton(введена из-за бага, который некорректно работает в super_user_registratin)
    cancel_reg_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_reg_keyboard.add("Отменить регистрацию")

    cancel_keyboard = ReplyKeyboardMarkup(resize_keyboard = True)
    cancel_keyboard.add("Отменить")

    @classmethod
    def get_keyboard(cls, role: str) -> ReplyKeyboardMarkup:
        if role == "admin":
            return cls.admin_keyboard
        else:
            return cls.keyboard

