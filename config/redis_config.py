import redis
from aiogram.fsm.storage.redis import RedisStorage

# Create the client
client = RedisStorage(redis)
