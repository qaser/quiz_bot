from aiogram import Bot, Dispatcher
from config.telegram_config import TELEGRAM_TOKEN
from config.redis_config import storage


bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(storage=storage)
