from sqlalchemy import create_engine, Column, Integer, String, Date, BigInteger
from sqlalchemy.orm import declarative_base, sessionmaker
from aiogram import types
from bot.config import config
from datetime import datetime
import logging

logger = logging.getLogger("bot.bd")
logger.setLevel(logging.INFO)

DATABASE_URL = config.DATABASE_URL
# Создание движка подключения
engine = create_engine(DATABASE_URL)

# Базовый класс для декларативных моделей
Base = declarative_base()

# Создание сессии
Session = sessionmaker(bind=engine)
session = Session()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False)
    birthday_date = Column(Date)
    user_id = Column(BigInteger, nullable=False)
    user_username = Column(String(30), unique=True, nullable=False)

    def __repr__(self):
        return (f'<User(id={self.id}, name={self.name}, user_id={self.user_id}, '
                f'user_username={self.user_username}, birthday_date={self.birthday_date})>')

Base.metadata.create_all(engine)

def new_user(name: str, user_id: int, birthday_date: datetime.date, user_username: str):
    if user_exists(user_id):
        logger.info(f"Пользователь с user_id={user_id} уже существует.")
        return
    new_user = User( name = name, user_id = user_id, birthday_date = birthday_date, user_username = user_username )
    session.add(new_user)
    session.commit()
    logger.info(f"Добавлен новый пользователь: {new_user}")

def user_exists(user_id: int) -> bool:
    return session.query(User).filter(User.user_id == user_id).first() is not None

async def get_all_users(message: types.Message):
    users = session.query(User).all()
    if users:
        user_list = "\n".join([f"{user.name},@{user.user_username},(ID:{user.user_id})" for user in users])
        await message.reply(f"Список пользователей:\n{user_list}")
    else:
        await message.reply("В базе данных нет пользователей.")

async def get_all_birthdays(message: types.Message):
    birthdays = session.query(User).filter(User.birthday_date.isnot(None)).all()
    if birthdays:
        birthday_list = "\n".join([f"{b.name}, {b.birthday_date.strftime('%d.%m')}" for b in birthdays])
        await message.reply(f"Список дней рождений:\n{birthday_list}")
    else:
        await message.reply("В базе данных нет дней рождений.")

Base = declarative_base()

class SuperUser(Base):
    __tablename__ = 'super_users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    birthday_date = Column(Date, nullable=False)
    super_user_id = Column(BigInteger, unique=True, nullable=False)

    def __repr__(self):
        return f"<SuperUser(id={self.id}, name={self.name}, birthday_date={self.birthday_date}, super_user_id={self.super_user_id})>"

Base.metadata.create_all(engine)

def new_sup_user(name: str, super_user_id: int, birthday_date: datetime.date):
    new_user = SuperUser(name = name, super_user_id = super_user_id, birthday_date = birthday_date)
    session.add(new_user)
    session.commit()
    logger.info(f"Добавлен новый пользователь: {new_user}")

async def Sup_get_all_birthdays(message: types.Message):
    user_id = message.from_user.id
    birthdays = session.query(SuperUser).filter(SuperUser.birthday_date.isnot(None), SuperUser.super_user_id == user_id).all()

    if birthdays:
        birthday_list = "\n".join([f"{b.name}, {b.birthday_date.strftime('%d.%m')}" for b in birthdays])
        await message.reply(f"Список ваших дней рождений:\n{birthday_list}")
    else:
        await message.reply("Для вас нет доступных дней рождений.")






