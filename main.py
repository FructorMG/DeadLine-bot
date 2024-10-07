import logging
import asyncio
from aiogram import executor
from bot.bot import dp
from bot import setup_middlewares, setup_handlers
from bot.Services.scheduler import scheduled_check

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("bot")

async def on_startup(dispatcher):
    logger.info("Бот запущен и готов к работе.")
    setup_middlewares()
    setup_handlers()
    asyncio.create_task(scheduled_check())

if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, on_startup=on_startup)
