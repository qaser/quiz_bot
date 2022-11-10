import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')  # тестовый чат
MY_TELEGRAM_ID = os.getenv('MY_TELEGRAM_ID')
