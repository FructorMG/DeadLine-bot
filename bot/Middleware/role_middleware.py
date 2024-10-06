import logging
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message
from bot.config import config

logger = logging.getLogger("bot")

class RoleMiddleware(BaseMiddleware):
    def __init__(self):
        super(RoleMiddleware, self).__init__()

    async def on_process_message(self, message: Message, data: dict):
        user_id = message.from_user.id
        if user_id in config.admins_list:
            message.role = 'admin'
        elif user_id in config.assistants_list:
            message.role = 'assistant'
        elif user_id in config.super_users_list:
            message.role = 'super_users'
        else:
            message.role = 'user'
