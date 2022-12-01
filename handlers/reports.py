import datetime as dt
from math import ceil
import os
import pprint

from config.bot_config import bot, dp
from config.telegram_config import ADMIN_TELEGRAM_ID
from config.mongo_config import users, questions, plans, results
from scheduler.scheduler_func import send_quiz_button
from utils.utils import calc_date, calc_grade, calc_test_type, word_conjugate
from utils.decorators import admin_check
from utils.make_pdf import report_department_pdf

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class DepartmentReport(StatesGroup):
    waiting_year = State()
    waiting_quarter = State()


@admin_check
async def department_report(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    user_id = message.from_user.id
    years = results.distinct('year')
    buttons = [types.InlineKeyboardButton(
        text=str(year),
        callback_data=f'report_year_{year}_{user_id}'
    ) for year in years]
    keyboard.add(*buttons)
    await message.answer('Выберите отчётный год', reply_markup=keyboard)


@dp.callback_query_handler(Text(startswith='report_year_'))
async def get_year(call: types.CallbackQuery):
    _, _, year, user_id = call.data.split('_')
    await call.message.delete_reply_markup()
    await bot.send_message(chat_id=user_id, text=f'Вы выбрали {year} год')
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    buttons = [types.InlineKeyboardButton(
        text=str(q),
        callback_data=f'report_quarter_{q}_{year}_{user_id}'
    ) for q in range(1,5)]
    keyboard.add(*buttons)
    await bot.send_message(
        chat_id=user_id,
        text='Выберите квартал',
        reply_markup=keyboard,
    )


@dp.callback_query_handler(Text(startswith='report_quarter_'))
async def get_quarter(call: types.CallbackQuery):
    _, _, q, year, user_id = call.data.split('_')
    await call.message.delete_reply_markup()
    await bot.send_message(chat_id=user_id, text=f'Вы выбрали {q} квартал')
    await bot.send_message(chat_id=user_id, text='Отчёт формируется, ожидайте')
    await get_results(year, q, user_id)


async def get_results(year, quarter, user_id):
    user = users.find_one({'user_id': int(user_id)})
    department = user.get('department')
    users_set = list(users.find({'department': department}))
    results_set = []
    for u in users_set:
        res = {}
        res_input = results.find_one(
            {
                'user_id': u.get('user_id'),
                'year': int(year),
                'quarter': int(quarter),
                'done': 'true',
                'test_type': 'input'
            }
        )
        res_output = results.find_one(
            {
                'user_id': u.get('user_id'),
                'year': int(year),
                'quarter': int(quarter),
                'done': 'true',
                'test_type': 'output'
            }
        )
        res['user'] = u.get('full_name')
        if res_input is not None:
            res['date_input'] = res_input.get('date_end')
            res['grade_input'] = res_input.get('grade')
        else:
            res['date_input'] = '-'
            res['grade_input'] = '-'
        if res_output is not None:
            res['date_output'] = res_output.get('date_end')
            res['grade_output'] = res_output.get('grade')
        else:
            res['date_output'] = '-'
            res['grade_output'] = '-'
        results_set.append(res)
    await send_result(year, quarter, department, user_id, results_set)


async def send_result(year, quarter, department, user_id, results_set):
    report_department_pdf(year, quarter, department, results_set)
    path = f'static/reports/Отчёт ТУ {department} {quarter} кв. {year}г.pdf'
    await bot.send_document(
        chat_id=user_id,
        document=open(path, 'rb')
    )
    os.remove(path)


def register_handlers_reports(dp: Dispatcher):
    dp.register_message_handler(department_report, commands='report')
