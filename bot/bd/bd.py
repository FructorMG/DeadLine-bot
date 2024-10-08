from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import declarative_base, sessionmaker
from aiogram import types
from bot.config import config
from datetime import datetime


DATABASE_URL = config.DATABASE_URL
# Создание движка подключения
engine = create_engine(DATABASE_URL)

# Базовый класс для декларативных моделей
Base = declarative_base()

# Создание сессии
Session = sessionmaker(bind=engine)
session = Session()
class DataBase(Base):
    __tablename__ = 'users'
    id = Column(Integer, primery_key = True)
    name = Column(String, nullable = False)
    user_id = Column(String, unique = True, nullable = False)
    birth_date = Column(Date, unique=True, nullable=False)
    def __repr__(self):
        return (f'<User(id = {self.id}, username = {self.name}, user_id = '
                f'{self.user_id}, birthday = {self.birth_date}')
def user_exists(user_id: str) -> bool:
    return session.query(DataBase).filter(DataBase.user_id == user_id).first() is not None
def new_user(username: str, user_id: str):
    if user_exists(user_id):
        return
    new_user = DataBase(name=username, user_id=user_id)
    session.add(new_user)
    session.commit()
async def get_all_users(message: types.Message):
    users = session.query(DataBase).all()
    if users:
        user_list = "\n".join([f"{user.name}, {user.user_id}" for user in users])
        await message.reply(f"Список пользователей:\n{user_list}")
    else:
        await message.reply("В базе данных нет пользователей.")
async def get_all_birthdays(message: types.Message):
    birthdays = session.query(DataBase).all()
    if birthdays:
        birthday_list = "\n".join([ f"{b.name}, {b.birth_date.strftime('%d.%m')}," for b in birthdays])
        await message.reply(f"Список дней рождений:\n{birthday_list}")
    else:
        await message.reply("В базе данных нет дней рождений.")




#class User(Base):
 #   __tablename__ = 'users_id'
 #   id = Column(Integer, primary_key=True)
 #   name = Column(String, nullable=False)
  #  user_id = Column(String, unique=True, nullable=False)
  #  def __repr__(self):
   #     return f"<User(id={self.id}, username={self.name}, user_id={self.user_id})>"


#class Birthdays(Base):
 #   __tablename__ = 'birthdays'
  #  id = Column(Integer, primary_key=True)
   # name = Column(String, nullable=False)
    #birth_date = Column(Date, unique=True, nullable=False)
    #def __repr__(self):
#        return f"<User(id={self.id}, username={self.name}, date={self.birth_date})>"
#def birthdays_exists(birth_date: str) -> bool:
#    return session.query(Birthdays).filter(Birthdays.birth_date == birth_date).first() is not None



