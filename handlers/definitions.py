import datetime as dt

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from config.bot_config import bot, dp
from config.mongo_config import offers, users
from config.telegram_config import ADMIN_TELEGRAM_ID
from utils.decorators import superuser_check
from utils.constants import METAN


async def natural_gas(message: types.Message):
    if message.text == 'газ':
        await message.answer(METAN)


def register_handlers_definitions(dp: Dispatcher):
    dp.register_message_handler(natural_gas)
