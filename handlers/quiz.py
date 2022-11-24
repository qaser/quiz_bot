import datetime as dt
from math import ceil

from config.bot_config import bot, dp
from config.telegram_config import ADMIN_TELEGRAM_ID
from config.mongo_config import users, questions, plans, results
from scheduler.scheduler_func import send_quiz_button
from utils.utils import calc_date, calc_grade, calc_test_type

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


'''
Сделать протоколы проверки знаний в формате pdf

Сделать отчёт о прохождении входного/выходного теста по истечению квартала
со сравнением входа и выхода

'''

@dp.callback_query_handler(Text(startswith='quiz_'))
async def get_questions(call: types.CallbackQuery):
    date_start = dt.datetime.now().strftime('%d.%m.%Y')
    _, id = call.data.split('_')
    user_id = int(id)
    year, month, quarter = calc_date()
    test_type = calc_test_type(month)
    department = users.find_one({'user_id': user_id}).get('department')
    questions_ids = plans.find_one({
        'year': year,
        'quarter': quarter,
        'department': department
    }).get('questions')
    res_id = results.insert_one({
        'user_id': user_id,
        'year': year,
        'quarter': quarter,
        'test_type': test_type,
        'done': 'false',
        'q_len': len(questions_ids),
        'count': 0,
        'q_ids': questions_ids,
        'quiz': '',
        'quiz_results': [],
        'date_start': date_start,
    })
    await call.message.delete_reply_markup()
    await send_quiz(res_id.inserted_id)


async def send_quiz(res_id):
    data = results.find_one({'_id': res_id})
    count = data.get('count')
    q_len = data.get('q_len')
    if count < q_len:
        q_ids = data.get('q_ids')
        q_id = q_ids[count]
        q = questions.find_one({'_id': q_id})
        correct_id = q.get('correct_answer') - 1
        quiz = await bot.send_poll(
            chat_id=data.get('user_id'),
            type='quiz',
            question=q.get('question'),
            options=q.get('answers'),
            is_anonymous=False,
            correct_option_id=correct_id,
            protect_content=True
        )
        results.update_one(
            {'_id': res_id},
            {'$set': {'quiz': quiz.poll.id, 'count': count + 1}},
            upsert=False
        )
    else:
        await bot.send_message(
            data.get('user_id'),
            'Тестирование окончено'
        )
        await save_result(res_id)


@dp.poll_answer_handler()
async def handle_quiz_answer(quiz_answer: types.PollAnswer):
    data = results.find_one({
        'user_id': quiz_answer.user.id,
        'quiz': quiz_answer.poll_id
    })
    q_num = data.get('count') - 1
    q_id = data.get('q_ids')[q_num]
    q = questions.find_one({'_id': q_id})
    correct_ans = q.get('correct_answer') - 1
    quiz_result = data.get('quiz_results')
    res = 'true' if correct_ans == quiz_answer.option_ids[0] else 'false'
    quiz_res = (q_id, correct_ans, quiz_answer.option_ids[0], res)
    quiz_result.append(quiz_res)
    results.update_one(
        {'_id': data.get('_id')},
        {'$set': {'quiz_results': quiz_result, 'done': 'true'}},
        upsert=False
    )
    await send_quiz(data.get('_id'))


async def save_result(res_id):
    date_end = dt.datetime.now().strftime('%d.%m.%Y')
    data = results.find_one({'_id': res_id})
    quiz_results = data.get('quiz_results')
    count_pos_ans = [x[3] for x in quiz_results].count('true')
    grade = calc_grade(count_pos_ans, len(quiz_results))
    results.update_one(
        {'_id': res_id},
        {
            '$set': {'date_end': date_end, 'grade': grade},
            '$unset': {
                'q_len': True,
                'count': True,
                'q_ids': True,
                'quiz': True
            }
        },
        upsert=False
    )
    await bot.send_message(data.get('user_id'), f'Ваш результат: {grade}')


async def send_quiz_to_users(message: types.Message):
    await send_quiz_button()


def register_handlers_quiz(dp: Dispatcher):
    dp.register_message_handler(send_quiz_to_users, commands='quiz')
