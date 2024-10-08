from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from aiogram import types
from bot.config import config

DATABASE_URL = config.DATABASE_URL
# Создание движка подключения
engine = create_engine(DATABASE_URL)

# Базовый класс для декларативных моделей
Base = declarative_base()

# Создание сессии
Session = sessionmaker(bind=engine)
session = Session()

class User(Base):
    __tablename__ = 'users_id'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    user_id = Column(String, unique=True, nullable=False)
    def __repr__(self):
        return f"<User(id={self.id}, username={self.name}, user_id={self.user_id})>"
def user_exists(user_id: str) -> bool:
    return session.query(User).filter(User.user_id == user_id).first() is not None


def new_user(username: str, user_id: str):
    if user_exists(user_id):
        return
    new_user = User(name=username, user_id=user_id)
    session.add(new_user)
    session.commit()


async def get_all_users(message: types.Message):
    users = session.query(User).all()
    if users:
        user_list = "\n".join([f"{user.name}, {user.user_id}" for user in users])
        await message.reply(f"Список пользователей:\n{user_list}")
    else:
        await message.reply("В базе данных нет пользователей.")

