from aiogram import Bot, Dispatcher

from config.mongo_config import storage
from config.telegram_config import TELEGRAM_TOKEN

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot, storage=storage)
