from bot.bot import dp
from bot.Middleware import RoleMiddleware
from bot.Handlers import *
from bot.Keyboards import *
from bot.Utils import *
from bot.Services import *

def setup_middlewares():
    dp.middleware.setup(RoleMiddleware())

def setup_handlers():
    pass
