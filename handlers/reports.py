import os
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from config.bot_config import bot
from config.mongo_config import results, users
from utils.decorators import admin_check
from utils.make_pdf import report_department_pdf
from utils.save_docx_file import create_results_docx_file
import keyboards.for_reports as kb


router = Router()


@admin_check
@router.message(Command('report'))
async def department_report(message: Message):
    user_id = message.from_user.id
    years = results.distinct('year')
    await message.delete()
    await message.answer(
        'Выберите отчётный год',
        reply_markup=kb.years_menu(years, user_id, 'report')
    )


@router.callback_query(F.data.startswith('report_y_'))
async def get_year(call: CallbackQuery):
    _, _, year, user_id = call.data.split('_')
    await call.message.edit_text(
        text=f'Вы выбрали {year} год.\nВыберите квартал',
        reply_markup=kb.quarters_menu(year, user_id, 'report'),
    )


@router.callback_query(F.data.startswith('report_q_'))
async def get_quarter(call: CallbackQuery):
    _, _, q, year, user_id = call.data.split('_')
    await call.message.edit_text(
        f'Вы выбрали {year} год, {q} квартал.\nОтчёт формируется, ожидайте'
    )
    await get_report(year, q, user_id)


async def get_report(year, quarter, user_id):
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
                'test_type': 'input',
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
    await send_report(year, quarter, department, user_id, results_set)


async def send_report(year, quarter, department, user_id, results_set):
    report_department_pdf(year, quarter, department, results_set)
    path = f'static/reports/Отчёт ТУ {department} ({quarter} кв. {year}г).pdf'
    await bot.send_document(chat_id=user_id, document=open(path, 'rb'))
    os.remove(path)


@admin_check
@router.message(Command('results'))
async def testing_results(message: Message):
    user_id = message.from_user.id
    years = results.distinct('year')
    await message.delete()
    await message.answer(
        'Выберите отчётный год',
        reply_markup=kb.years_menu(years, user_id, 'results')
    )


@router.callback_query(F.data.startswith('results_y_'))
async def results_get_year(call: CallbackQuery):
    _, _, year, user_id = call.data.split('_')
    await call.message.edit_text(
        text=f'Вы выбрали {year} год.\nВыберите квартал',
        reply_markup=kb.quarters_menu(year, user_id, 'results'),
    )


@router.callback_query(F.data.startswith('results_q_'))
async def results_get_quarter(call: CallbackQuery):
    _, _, q, year, user_id = call.data.split('_')
    await call.message.edit_text(
        text=f'Вы выбрали {year} год, {q} квартал.\nВыберите тип теста',
        reply_markup=kb.type_test_menu(year, user_id, q),
    )


@router.callback_query(F.data.startswith('results_t_'))
async def results_get_test_type(call: CallbackQuery):
    _, _, test_type, q, year, user_id = call.data.split('_')
    await call.message.edit_text(
        (f'Вы выбрали {year} год, {q} квартал, {test_type} тест.\n'
          'Документация формируется, ожидайте.')
    )
    await get_results(year, q, test_type, user_id)


async def get_results(year, quarter, test_type, user_id):
    TEST_TRANSLATE = {
        'входной': ('input', 'входного'),
        'выходной': ('output', 'выходного')
    }
    user = users.find_one({'user_id': int(user_id)})
    department = user.get('department')
    users_set = list(users.find({'department': department}))
    t_type, t_type_rus = TEST_TRANSLATE.get(test_type)
    results_set = []
    for u in users_set:
        res = results.find_one(
            {
                'user_id': u.get('user_id'),
                'year': int(year),
                'quarter': int(quarter),
                'test_type': t_type,
                'done': 'true'
            }
        )
        if res is not None:
            results_set.append(res)
    await send_results(year, quarter, t_type_rus, department, user_id, results_set)


async def send_results(year, quarter, test_type, department, user_id, results_set):
    create_results_docx_file(year, quarter, test_type, department, results_set)
    path = f'static/reports/Результаты {test_type} контроля знаний ({quarter} кв. {year}г).docx'
    await bot.send_document(
        chat_id=user_id,
        document=open(path, 'rb')
    )
    os.remove(path)
