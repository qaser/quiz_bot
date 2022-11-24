import datetime as dt
from math import ceil
from aiogram import Dispatcher, types

from config.mongo_config import plans, questions, users
from config.bot_config import bot
from config.telegram_config import ADMIN_TELEGRAM_ID
from utils.utils import calc_date


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


async def send_quiz_button():
    keyboard = types.InlineKeyboardMarkup()
    year, _, quarter = calc_date()
    queryset = list(plans.find({'year': year, 'quarter': quarter,}))
    departments = [dep.get('department') for dep in queryset]
    user_ids = []
    for dep in departments:
        ids = [user.get('user_id') for user in list(users.find({'department': dep}))]
        user_ids += ids
    for user_id in user_ids:
        keyboard.add(
            types.InlineKeyboardButton(
                text='Пройти тестирование',
                callback_data=f'quiz_{user_id}'
            )
        )
        try:
            await bot.send_message(
                chat_id=user_id,
                text='Пройдите тестирование нажав кнопку /quiz',
                reply_markup=keyboard,
            )
        except:
            bot.send_message(
                ADMIN_TELEGRAM_ID,
                f'Пользователь {user_id} не доступен'
            )


async def send_input_quiz():
    pass


async def send_output_quiz():
    pass
