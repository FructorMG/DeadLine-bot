import logging
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message
from bot.config import config
from bot.bd import ban_list, BannedUser
from aiogram.dispatcher.handler import CancelHandler
from typing import List

logger = logging.getLogger("bot.middlewares")

class RoleMiddleware(BaseMiddleware):
    def __init__(self):
        super(RoleMiddleware, self).__init__()

    async def on_process_message(self, message: Message, data: dict):
        user_id = message.from_user.id
        banned_users: List[BannedUser] = await ban_list()
        banned_user_ids = {user.banned_id for user in banned_users}
        if user_id in banned_user_ids:
            data["role"] = "banned"
            await message.reply("Вы заблокированы и не можете использовать этот бот.")
            raise CancelHandler()
        if user_id in config.admins_list:
            data["role"] = "admin"
        elif user_id in config.assistants_list:
            data["role"] = "assistant"
        elif user_id in config.super_users_list:
            data["role"] = "super_users"
        else:
            data["role"] = "user"
