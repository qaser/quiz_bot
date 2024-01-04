import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
ADMIN_TELEGRAM_ID = os.getenv('ADMIN_TELEGRAM_ID')
PASSWORD = os.getenv('PASSWORD')
CHAT_56_ID = os.getenv('CHAT_56_ID')
QUIZ_THREAD_ID = os.getenv('QUIZ_THREAD_ID')
