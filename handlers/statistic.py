import datetime as dt
import os

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from config.bot_config import bot, dp
from config.mongo_config import offers, users, key_rules, attentions, results
from config.telegram_config import ADMIN_TELEGRAM_ID
from utils.decorators import superuser_check, admin_check
from utils.utils import calc_date, calc_test_type


@admin_check
async def stat_now(message: types.Message):
    department = users.find_one({'user_id': message.from_user.id}).get('department')
    dep_users = list(users.find({'department': department}))
    year, month, quarter = calc_date()
    test_type = calc_test_type(month)
    queryset = list(results.find(
        {
            'year': year,
            'quarter': quarter,
            'test_type': test_type,
            'done': 'true'
        }
    ))
    done = []
    undone = []
    for user in dep_users:
        user_id = user.get('user_id')
        for res in queryset:
            if user_id == res.get('user_id'):
                done.append(user.get('user_id'))
        if user_id not in done:
            undone.append(user)
    if list(undone) == 0:
        await message.answer(f'Текущие тесты прошли все пользователи')
    else:
        users_list = ''
        for u in undone:
            users_list = f'{users_list}\n{u.get("full_name")}'
        await message.answer(f'Текущие тесты не прошли:\n{users_list}')


def register_handlers_statistic(dp: Dispatcher):
    dp.register_message_handler(stat_now, commands='stat_now')
