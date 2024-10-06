import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
ASSISTANTS = os.getenv('SUPPORT_ID')

ADMIN_IDS = os.getenv("ADMIN_IDS").split(",")
ADMINS = [int(admin_id.strip()) for admin_id in ADMIN_IDS]
print (ADMINS)
SUPER_USER_IDS = os.getenv("SUPER_USER_IDS").split(",")
SUPER_USERS = [int(super_user_id.strip()) for super_user_id in SUPER_USER_IDS]
print (SUPER_USERS)
if not BOT_TOKEN:
    logger.error("Не найден BOT_TOKEN в переменных окружения.")
    raise ValueError("Не найден BOT_TOKEN в переменных окружения.")
if not CHAT_ID:
    logger.error("Не найден CHAT_ID в переменных окружения.")
    raise ValueError("Не найден CHAT_ID в переменных окружения.")
if not ASSISTANTS:
    logger.info("СИСТЕМА: ОТСУТСВУЕТ SUPPORT_ID в переменных окружения ")
if not ADMINS:
    logger.info("СИСТЕМА: ОТСУТСВУЕТ ADMIN_ID в переменных окружения ")
if not SUPER_USERS:
    logger.info("СИСТЕМА: ОТСУТСВУЕТ SUPER_USER в переменных окружения ")



