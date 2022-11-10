import logging

from aiogram import types
from aiogram.utils import executor

from config.bot_config import bot, dp
from config.mongo_config import users
from config.telegram_config import MY_TELEGRAM_ID
from handlers.quiz import register_handlers_quiz
from handlers.service import register_handlers_service
from scheduler.scheduler_jobs import scheduler, scheduler_jobs
from texts.initial import INITIAL_TEXT

logging.basicConfig(
    filename='logs_bot.log',
    level=logging.INFO,
    filemode='a',
    format='%(asctime)s - %(message)s',
    datefmt='%d.%m.%y %H:%M:%S',
    encoding='UTF-8'
)


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user = message.from_user
    # проверяю есть ли пользователь в БД, если нет - добавляю
    check_user = users.find_one({'id': user.id})
    if check_user is None:
        users.insert_one({
            'user_id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.full_name,
            'username': user.username,
            'department': '',
        })
        await bot.send_message(
            chat_id=MY_TELEGRAM_ID,
            text=f'Добавлен новый пользователь в БД:\n{user.full_name}'
        )
    await message.answer(text=INITIAL_TEXT)



@dp.message_handler(commands=['help'])
async def help_handler(message: types.Message):
    await bot.send_message(
        message.chat.id,
        text=f'{message.from_user.full_name}{HELP_TEXT}'
    )
    await bot.send_message(message.chat.id, text=FINAL_TEXT)


@dp.message_handler(commands=['menu'])
async def all_commands(message: types.Message):
    await bot.send_message(message.chat.id, text=FINAL_TEXT)


async def on_startup(_):
    scheduler_jobs()


if __name__ == '__main__':
    scheduler.start()
    register_handlers_service(dp)
    register_handlers_quiz(dp)
    register_handlers_labor_safety(dp)
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
