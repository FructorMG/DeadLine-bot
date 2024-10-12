from bot.bot import dp
from bot.Middleware import RoleMiddleware, ThrottlingMiddleware

from bot.Handlers import *
from bot.Keyboards import *
from bot.Utils import *
from bot.Services import *

def setup_middlewares():
    dp.middleware.setup(RoleMiddleware())
    dp.middleware.setup(ThrottlingMiddleware())
def setup_handlers():
    UserRegistration()
    SuperUserRegistration()
