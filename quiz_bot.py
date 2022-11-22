import logging

from aiogram import types
from aiogram.utils import executor

from config.bot_config import dp
from handlers.admin_registration import register_handlers_admin_registration
# from config.mongo_config import users
# from config.telegram_config import ADMIN_TELEGRAM_ID
from handlers.plan import register_handlers_plan
from handlers.quiz import register_handlers_quiz
from handlers.registration import register_handlers_registration
from handlers.service import register_handlers_service
from scheduler.scheduler_jobs import scheduler, scheduler_jobs
from texts.initial import INITIAL_TEXT

logging.basicConfig(
    filename='logs_bot.log',
    level=logging.INFO,
    filemode='a',
    format='%(asctime)s - %(message)s',
    datefmt='%d.%m.%y %H:%M:%S',
    encoding='utf-8',
)


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.answer(text=INITIAL_TEXT)


async def on_startup(_):
    scheduler_jobs()


if __name__ == '__main__':
    scheduler.start()
    register_handlers_service(dp)
    register_handlers_registration(dp)
    register_handlers_admin_registration(dp)
    register_handlers_plan(dp)
    register_handlers_quiz(dp)
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
