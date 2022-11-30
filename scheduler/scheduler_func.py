import datetime as dt
from math import ceil
from aiogram import Dispatcher, types

from config.mongo_config import plans, questions, users
from config.bot_config import bot
from config.telegram_config import ADMIN_TELEGRAM_ID
from utils.constants import TEST_TYPE
from utils.utils import calc_date, calc_test_type
from utils.make_pdf import report_department_pdf

# формирование списка вопросов согласно тем плана
async def add_questions_in_plan():
    year, _, quarter = calc_date()
    plans_queryset = list(plans.find({'year': year, 'quarter': quarter}))
    for plan in plans_queryset:
        themes = plan.get('themes')
        res = []
        for theme in themes:
            list_questions = list(questions.aggregate(
                [{'$match': {'theme': theme}}, {'$sample': {'size': 10}}]
            ))
            q_ids = [q.get('_id') for q in list_questions]
            res = res + q_ids
        plans.update_one(
            {'_id': plan.get('_id')},
            {'$set': {'questions': res}}
        )
    await bot.send_message(ADMIN_TELEGRAM_ID, 'Тесты сформированы')


# отправка кнопки для начала тестирования
async def send_quiz_button():
    keyboard = types.InlineKeyboardMarkup()
    year, month, quarter = calc_date()
    test_type = TEST_TYPE.get(calc_test_type(month))
    queryset = list(plans.find({'year': year, 'quarter': quarter,}))
    departments = [dep.get('department') for dep in queryset]
    user_ids = []
    for dep in departments:
        ids = [user.get('user_id') for user in list(users.find({'department': dep}))]
        user_ids += ids
    for user_id in user_ids:
        keyboard.add(
            types.InlineKeyboardButton(
                text=f'Начать тестирование',
                callback_data=f'quiz_{user_id}'
            )
        )
        try:
            await bot.send_message(
                chat_id=user_id,
                text=(
                    f'Пройдите {test_type} тест знаний по '
                    f'плану технической учёбы {quarter}-го квартала.'
                ),
                reply_markup=keyboard,
            )
        except:
            bot.send_message(
                ADMIN_TELEGRAM_ID,
                f'Пользователь {user_id} не доступен'
            )
