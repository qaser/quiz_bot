from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from config.bot_config import dp
from config.mongo_config import (pb_answers, pb_program_groups,
                                 pb_questions, pb_users_stats, pb_rpo_program, pb_rpo_isp_program)
from utils.constants import TEST_TEXT


class Searching(StatesGroup):
    waiting_search_text = State()


def get_learning_question(count, employee):
    if employee == 'isp':
        q_id = pb_rpo_isp_program.find_one({'count': count}).get('id_question')
        num = 129
    else:
        q_id = pb_rpo_program.find_one({'count': count}).get('id_question')
        num = 2243
    q_text = pb_questions.find_one({'p_id': q_id}).get('text')
    a_text = pb_answers.find_one({'id_questions': q_id, 'correct_answer': 1}).get('answer')
    return f'Вопрос №{count} из {num}\n\n<b>{q_text}</b>\n\n{a_text}'


def get_full_learning_question(id, count):
    q_text = pb_questions.find_one({'p_id': id}).get('text')
    a_text = list(pb_answers.find({'id_questions': id, 'correct_answer': 1}))
    return f'Вопрос №{count} из 2243\n\n<b>{q_text}</b>\n\n{a_text}'


async def send_learning_question(message:types.Message, count, employee):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            text='Завершить',
            callback_data=f'learning_finish_{employee}_{count}'
        ),
        types.InlineKeyboardButton(
            text='Следующий',
            callback_data=f'learning_next_{employee}_{count+1}'
        ),
    )
    pb_users_stats.update_one(
        {'user_id': message.from_user.id},
        {'$set': {'question_count': count}}
    )
    text = get_learning_question(count, employee)
    await message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode=types.ParseMode.HTML
    )


@dp.callback_query_handler(Text(startswith='learning_'))
async def learning_choice(call: types.CallbackQuery):
    _, choice, employee, count = call.data.split('_')
    if choice == 'finish':
        pb_users_stats.update_one(
            {'user_id': call.message.from_user.id},
            {'$set': {'question_count': int(count)}}
        )
        await call.message.delete()
    elif choice == 'next':
        text = get_learning_question(int(count), employee)
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                text='Завершить',
                callback_data=f'learning_finish_{employee}_{count}'
            ),
            types.InlineKeyboardButton(
                text='Следующий',
                callback_data=f'learning_next_{employee}_{int(count)+1}'
            ),
        )
        await call.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode=types.ParseMode.HTML
        )


async def get_testing_questions(message: types.Message, employee):
    user_id = message.from_user.id
    user_stats = pb_users_stats.find_one({'user_id': user_id})
    if user_stats is None:
        pb_users_stats.insert_one(
            {'user_id': user_id, 'test_question_count': 0, 'test_result': []}
        )
    if employee == 'isp':
        rand_questions_query = list(pb_rpo_isp_program.aggregate([{ '$sample': { 'size': 20 } }]))
    else:
        rand_questions_query = list(pb_rpo_program.aggregate([{ '$sample': { 'size': 20 } }]))
    rand_questions_ids = [q.get('id_question') for q in rand_questions_query]
    pb_users_stats.update_one(
        {'user_id': user_id},
        {'$set': {'test_quiz': rand_questions_ids, 'test_question_count': 0, 'test_result': []}}
    )
    await test_send_question(message)


async def test_send_question(message: types.Message):
    user_stats = pb_users_stats.find_one({'user_id': message.from_user.id})
    count = user_stats.get('test_question_count')
    if count == 19:
        test_result = user_stats.get('test_result')
        res = sum(1 for i in test_result if i == 1)
        pb_users_stats.update_one(
            {'user_id': message.from_user.id},
            {'$set': {'test_result': [], 'test_question_count': 0}}
        )
        await message.edit_text(f'Тест завершён.\nПравильных ответов: {res} из 20-ти')
    else:
        keyboard = types.InlineKeyboardMarkup(row_width=5)
        question_id = user_stats.get('test_quiz')[count]
        question = pb_questions.find_one({'p_id': question_id})
        answers_query = list(pb_answers.find({'id_questions': question_id}))
        a_text = ''
        buttons = []
        for ans in answers_query:
            sort_num = ans.get('sort_number')
            text = ans.get('answer')
            a_text = f'{a_text}\n<b>{sort_num}</b>. {text}'
            btn = types.InlineKeyboardButton(
                text=sort_num,
                callback_data=f'answer_{ans.get("p_id")}_{question.get("p_id")}'
            )
            buttons.append(btn)
        keyboard.row(*buttons)
        q_text = question.get('text')
        await message.edit_text(
            f'<i>Вопрос №{count+1}\n</i><b>{q_text}</b>\n{a_text}',
            reply_markup=keyboard,
            parse_mode=types.ParseMode.HTML
        )


@dp.callback_query_handler(Text(startswith='answer_'))
async def answer_check(call: types.CallbackQuery):
    _, ans_id, q_id = call.data.split('_')
    ans_check = pb_answers.find_one({'p_id': int(ans_id)}).get('correct_answer')
    user_id = call.message.from_user.id
    user_stats = pb_users_stats.find_one({'user_id': user_id})
    test_result = user_stats.get('test_result')
    test_result.append(ans_check)
    test_count = user_stats.get('test_question_count') + 1
    pb_users_stats.update_one(
        {'user_id': user_id},
        {'$set': {'test_result': test_result, 'test_question_count': test_count}}
    )
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            text='Завершить',
            callback_data='testing_exit'
        ),
        types.InlineKeyboardButton(
            text='Следующий',
            callback_data='testing_next'
        ),
    )
    if ans_check == 1:
        text = 'Ответ верный'
    else:
        correct_ans = pb_answers.find_one(
            {'id_questions': int(q_id), 'correct_answer': 1}
        ).get('answer')
        text = f'Ответ неверный\n\n<b>Правильный ответ:</b>\n{correct_ans}'
    await call.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode=types.ParseMode.HTML
    )


@dp.callback_query_handler(Text(startswith='testing_'))
async def testing_check_choice(call: types.CallbackQuery):
    _, choice = call.data.split('_')
    user_id = call.message.from_user.id
    if choice == 'exit':
        pb_users_stats.update_one(
            {'user_id': user_id},
            {'$set': {'test_result': [], 'test_question_count': 0}}
        )
        await call.message.edit_text('Тест завершён, прогресс сброшен')
    elif choice == 'next':
        await test_send_question(call.message)


async def testing(message: types.Message, employee):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(text='Отмена', callback_data=f'test_{employee}_exit'),
        types.InlineKeyboardButton(text='Начать', callback_data=f'test_{employee}_start'),
    )
    await message.edit_text(TEST_TEXT, reply_markup=keyboard)


@dp.callback_query_handler(Text(startswith='test_'))
async def testing_choice(call: types.CallbackQuery):
    _, employee, choice = call.data.split('_')
    if choice == 'exit':
        await call.message.delete()
    elif choice == 'start':
        await get_testing_questions(call.message, employee)


async def learning(message: types.Message, employee):
    user_stats = pb_users_stats.find_one({'user_id': message.from_user.id})
    if user_stats is None:
        pb_users_stats.insert_one(
            {'user_id': message.from_user.id, 'question_count': 1}
        )
        await send_learning_question(message, 1, employee)
    else:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                text='Начать заново',
                callback_data=f'learn_{employee}_new'
            ),
            types.InlineKeyboardButton(
                text='Продолжить',
                callback_data=f'learn_{employee}_continue'
            ),
        )
        learn_count = user_stats.get('question_count')
        await message.edit_text(
            text=(f'В прошлый раз Вы остановились на вопросе #{learn_count}'),
            reply_markup=keyboard,
        )


@dp.callback_query_handler(Text(startswith='learn_'))
async def learn_choice(call: types.CallbackQuery):
    _, employee, choice = call.data.split('_')
    if choice == 'new':
        await send_learning_question(call.message, count=1, employee=employee)
    elif choice == 'continue':
        count = pb_users_stats.find_one({'user_id': call.message.from_user.id}).get('question_count')
        await send_learning_question(call.message, count, employee)


async def searching(message: types.Message):
    await message.answer(
        text=('Введите и отправьте текст вопроса для поиска. '
              'Чем больше слов Вы введете тем точнее выполнится поиск.'),
    )
    await message.delete()
    await Searching.waiting_search_text.set()


async def question_search(message: types.Message, state: FSMContext):
    await state.finish()
    q_search = list(pb_questions.find(
        {'$text': {'$search': f'\"{message.text}\"'}}
    ))
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Найти ещё', callback_data='search_next'),)
    len_search = len(q_search)
    if len_search == 0:
        await message.answer(
            f'Вопросов с таким текстом не найдено, попробуйте ввести больше слов.',
            reply_markup=keyboard
        )
    elif len_search == 1:
        q_id = q_search[0].get('p_id')
        ans = pb_answers.find_one({'id_questions': q_id, 'correct_answer': 1})
        q_text = pb_questions.find_one({'p_id': q_id}).get('text')
        ans_text = ans.get('answer')
        ans_id = ans.get('sort_number')
        await message.answer(
            f'Вопрос: {q_text}\n\nПравильный вариант ответа: {ans_id}\n{ans_text}',
            reply_markup=keyboard
        )
    else:
        for id, q in enumerate(q_search):
            if id == 2:
                break
            q_id = q.get('p_id')
            ans = pb_answers.find_one({'id_questions': q_id, 'correct_answer': 1})
            q_text = pb_questions.find_one({'p_id': q_id}).get('text')
            ans_text = ans.get('answer')
            ans_id = ans.get('sort_number')
            await message.answer(
                f'Вопрос: {q_text}\n\nПравильный вариант ответа: {ans_id}\n{ans_text}',
            )
        await message.answer(
            (f'Найдено вопросов: {len_search}. Выше показаны первые два результата.'
            ' Для уточнения результата попробуйте ввести больше слов.'
            '\nМожете скопировать Ваш запрос ниже и дополнить его.'),
            reply_markup=keyboard
        )
        await message.answer(message.text)



@dp.callback_query_handler(Text(startswith='search_'))
async def searching_choice(call: types.CallbackQuery):
    _, choice = call.data.split('_')
    if choice == 'exit':
        await call.message.delete()
    elif choice == 'next':
        await searching(call.message)


async def pb_select(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton(
            text='Поиск ответа по тексту вопроса',
            callback_data='rpo_none_search'
        )
    )
    keyboard.row(
        types.InlineKeyboardButton(
            text='Обучение для рабочих',
            callback_data='rpo_isp_learn'
        )
    )
    keyboard.row(
        types.InlineKeyboardButton(
            text='Самопроверка для рабочих',
            callback_data='rpo_isp_test'
        )
    )
    keyboard.row(
        types.InlineKeyboardButton(
            text='Обучение для ИТР',
            callback_data='rpo_itr_learn'
        )
    )
    keyboard.row(
        types.InlineKeyboardButton(
            text='Самопроверка для ИТР',
            callback_data='rpo_itr_test'
        )
    )
    # для нескольких програм обучения "p_id" нужно будет запрашивать у пользователя
    program_name = pb_program_groups.find_one({'p_id': 100000227}).get('title')
    await message.answer(
        text=f'{program_name}\n\nВыберите режим:',
        reply_markup=keyboard,
    )
    await message.delete()


@dp.callback_query_handler(Text(startswith='rpo_'))
async def get_mode(call: types.CallbackQuery):
    _, employee, mode = call.data.split('_')
    if mode == 'learn':
        await learning(call.message, employee)
    elif mode == 'test':
        await testing(call.message, employee)
    elif mode == 'search':
        await searching(call.message)


def register_handlers_pb(dp: Dispatcher):
    dp.register_message_handler(pb_select, commands='rpo')
    dp.register_message_handler(
        question_search,
        state=Searching.waiting_search_text,
    )
