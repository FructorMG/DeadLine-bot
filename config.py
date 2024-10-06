import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
SUPPORT_ID = os.getenv('SUPPORT_ID')
ADMIN_ID = os.getenv('ADMIN_ID')
if not BOT_TOKEN:
    logger.error("Не найден BOT_TOKEN в переменных окружения.")
    raise ValueError("Не найден BOT_TOKEN в переменных окружения.")
if not CHAT_ID:
    logger.error("Не найден CHAT_ID в переменных окружения.")
    raise ValueError("Не найден CHAT_ID в переменных окружения.")
if not SUPPORT_ID:
    logger.info("СИСТЕМА: ОТСУТСВУЕТ SUPPORT_ID в переменных окружения ")
if not ADMIN_ID:
    logger.info("СИСТЕМА: ОТСУТСВУЕТ ADMIN_ID в переменных окружения ")
try:
    ADMIN_ID = int(ADMIN_ID)
except (TypeError, ValueError):
    ADMIN_ID = None
    logger.warning("ADMIN_ID не установлен или некорректен.")


