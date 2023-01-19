# import datetime as dt
# import os

# from aiogram import Dispatcher, types
# from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters.state import State, StatesGroup

# from config.bot_config import bot, dp
# from config.mongo_config import offers, users, key_rules, attentions, results
# from config.telegram_config import ADMIN_TELEGRAM_ID
# from utils.decorators import superuser_check


# async def choose_year(message: types.Message):
#     keyboard = types.InlineKeyboardMarkup()
#     years = results.distinct('year')
#     for year in years:
#         keyboard.add(
#             types.InlineKeyboardButton(
#                 text=f'{year}',
#                 callback_data=f'attention_{year}'
#             )
#         )
#     await message.delete()
#     await message.answer('Выберите год', reply_markup=keyboard)
