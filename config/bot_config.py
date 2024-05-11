from aiogram import Bot, Dispatcher
from config.telegram_config import TELEGRAM_TOKEN
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder


storage = RedisStorage.from_url(
    'redis://localhost:6379/0',
    key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(storage=storage)
