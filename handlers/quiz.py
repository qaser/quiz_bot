import datetime as dt

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import CantInitiateConversation

from config.bot_config import bot, dp
from config.mongo_config import plans, questions, results, users
from config.telegram_config import ADMIN_TELEGRAM_ID
from scheduler.scheduler_func import send_quiz_button
from utils.utils import calc_grade, word_conjugate

'''
Сделать протоколы проверки знаний в формате pdf

'''


@dp.callback_query_handler(Text(startswith='quiz_'))
async def get_questions(call: types.CallbackQuery):
    # TODO сделать разделение на составление вопросов при типе теста 'special'
    # когда 'special' направить пользователя на выбор тем
    date_start = dt.datetime.now().strftime('%d.%m.%Y')
    _, year, quarter, test_type, id = call.data.split('_')
    user_id = int(id)
    department = users.find_one({'user_id': user_id}).get('department')
    questions_ids = plans.find_one({
        'year': int(year),
        'quarter': int(quarter),
        'department': department
    }).get('questions')
    res_id = results.insert_one({
        'user_id': user_id,
        'year': int(year),
        'quarter': int(quarter),
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
    user_id = data.get('user_id')
    count_pos_ans = [x[3] for x in quiz_results].count('true')
    len_quiz_res = len(quiz_results)
    grade = calc_grade(count_pos_ans, len_quiz_res)
    q_word = word_conjugate(count_pos_ans, ['вопрос', 'вопроса', 'вопросов'])
    g_word = word_conjugate(grade, ['балл', 'балла', 'баллов'])
    l_word = word_conjugate(len_quiz_res, ['-го', '-х', '-ти'])
    results.update_one(
        {'_id': res_id},
        {
            '$set': {'date_end': date_end, 'grade': grade},
            '$unset': {
                'q_len': True,
                'count': True,
                'q_ids': True,
                'quiz': True,
            }
        },
        upsert=False
    )
    await bot.send_message(
        chat_id=user_id,
        text=(
            'Тестирование завершено.\n'
            f'Вы ответили правильно на {count_pos_ans} {q_word} '
            f'из {len_quiz_res}{l_word}.\n'
            f'Ваш результат: {grade} {g_word}\n'
        )
    )
    await send_admin_notification(user_id)


async def send_admin_notification(user_id):
    user = users.find_one({'user_id': user_id})
    user_name = user.get('full_name')
    department = user.get('department')
    admins = list(users.find({'department': department, 'is_admin': 'true'}))
    if len(admins) > 0:
        for admin in admins:
            try:
                await bot.send_message(
                    chat_id=admin.get('user_id'),
                    text=f'Пользователь {user_name} прошёл тестирование'
                )
            except CantInitiateConversation:
                await bot.send_message(
                    chat_id=ADMIN_TELEGRAM_ID,
                    text=f'Пользователь "{user_name}" недоступен.'
                )
                continue


async def send_quiz_to_users(message: types.Message):
    await send_quiz_button()


def register_handlers_quiz(dp: Dispatcher):
    dp.register_message_handler(send_quiz_to_users, commands='quiz')
