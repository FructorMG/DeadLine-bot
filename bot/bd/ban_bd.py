from sqlalchemy import create_engine, Column, Integer, BigInteger
from sqlalchemy.orm import declarative_base, sessionmaker
from aiogram import types
from bot.config import config
from datetime import datetime
import logging


logger = logging.getLogger("bot.ban_bd")
logger.setLevel(logging.INFO)

DATABASE_URL = config.DATABASE_URL
# Создание движка подключения
engine = create_engine(DATABASE_URL)
# Базовый класс для декларативных моделей
Base = declarative_base()
# Создание сессии

Session = sessionmaker(bind=engine)
session = Session()

class BannedUser(Base):
    __tablename__ = 'ban_list'

    id = Column(Integer, primary_key=True, autoincrement=True)
    banned_id = Column(BigInteger, nullable=False)

    def __repr__(self):
        return (f'<User(id={self.id} user_id={self.banned_id}')
Base.metadata.create_all(engine)

def new_user(banned_id: BigInteger):
    new_user = BannedUser(banned_id = banned_id)
    session.add(new_user)
    session.commit()
    logger.info(f"Пользователь {new_user}был забанен")

async def get_ban_list(message: types.Message):
    ban_list = session.query(BannedUser).filter(BannedUser.banned_id.isnot(None)).all()
    if ban_list:
        ban_list_text = "\n".join([f"{i+1}. {b.banned_id}" for i, b in enumerate(ban_list)])
        await message.reply(f"Бан список:\n{ban_list_text}")
    else:
        await message.reply("Бан-лист пуст.")

