from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import keyboards.for_pb as kb

from config.mongo_config import (pb_answers, pb_program_groups, pb_questions,
                                 pb_rpo_isp_program, pb_rpo_program,
                                 pb_users_stats)

router = Router()


TEST_SIZE_ISP = 149
TEST_SIZE_ITR = 20


class Searching(StatesGroup):
    waiting_search_text = State()


def get_learning_question(count, employee):
    if employee == 'isp':
        num = pb_rpo_isp_program.count_documents({})
        if count > num:
            count = 1
        elif count == 0:
            count = num
        q_id = pb_rpo_isp_program.find_one({'count': count}).get('id_question')
    else:
        num = pb_rpo_program.count_documents({})
        if count > num:
            count = 1
        elif count == 0:
            count = num
        q_id = pb_rpo_program.find_one({'count': count}).get('id_question')
    q_text = pb_questions.find_one({'p_id': q_id}).get('text')
    # a_text = pb_answers.find_one({'id_questions': q_id, 'correct_answer': 1}).get('answer')
    answers = list(pb_answers.find({'id_questions': q_id}))
    ans_text = ''
    for ans in answers:
        a_text = ans.get('answer')
        a_num = ans.get('sort_number')
        if ans.get('correct_answer') == 1:
            ans_text = f'{ans_text}\n\n<b>{a_num}. {a_text}</b>'
        else:
            ans_text = f'{ans_text}\n\n{a_num}. {a_text}'
    return f'Вопрос №{count} из {num}\n\n<i>{q_text}</i>{ans_text}'


async def send_learning_question(message: Message, count, employee):
    pb_users_stats.update_one(
        {'user_id': message.chat.id},
        {'$set': {f'question_{employee}_count': count}}
    )
    text = get_learning_question(count, employee)
    await message.edit_text(
        text,
        reply_markup=kb.learn_menu(employee, count),
        parse_mode='HTML'
    )


@router.callback_query(F.data.startswith('learning_'))
async def learning_choice(call: CallbackQuery):
    _, choice, employee, count = call.data.split('_')
    if choice == 'finish':
        pb_users_stats.update_one(
            {'user_id': call.message.chat.id},
            {'$set': {f'question_{employee}_count': int(count)}}
        )
        await call.message.delete()
    elif choice == 'next':
        if employee == 'isp':
            num = pb_rpo_isp_program.count_documents({})
            if int(count) > num:
                count = 1
        else:
            num = pb_rpo_program.count_documents({})
            if int(count) > num:
                count = 1
        text = get_learning_question(int(count), employee)
        await call.message.edit_text(
            text,
            reply_markup=kb.learn_menu(employee, int(count)+1),
            parse_mode='HTML'
        )


async def get_testing_questions(message: Message, employee):
    user_id = message.chat.id
    user_stats = pb_users_stats.find_one({'user_id': user_id})
    if user_stats is None:
        pb_users_stats.insert_one(
            {'user_id': user_id, 'test_question_count': 0, 'test_result': []}
        )
    if employee == 'isp':
        rand_questions_query = list(pb_rpo_isp_program.find({}))
    elif employee == 'itr':
        rand_questions_query = list(pb_rpo_program.aggregate([{ '$sample': { 'size': TEST_SIZE_ITR } }]))
    rand_questions_ids = [q.get('id_question') for q in rand_questions_query]
    pb_users_stats.update_one(
        {'user_id': user_id},
        {'$set': {'test_quiz': rand_questions_ids, 'test_question_count': 0, 'test_result': []}}
    )
    await test_send_question(message, employee)


async def test_send_question(message: Message, employee):
    user_stats = pb_users_stats.find_one({'user_id': message.chat.id})
    count = user_stats.get('test_question_count')
    q_num = TEST_SIZE_ITR if employee == 'itr' else TEST_SIZE_ISP
    if count == q_num:
        test_result = user_stats.get('test_result')
        res = sum(1 for i in test_result if i == 1)
        pb_users_stats.update_one(
            {'user_id': message.chat.id},
            {'$set': {'test_result': [], 'test_question_count': 0}}
        )
        await message.edit_text(f'Тест завершён.\nПравильных ответов: {res} из {q_num}-ти')
    else:
        question_id = user_stats.get('test_quiz')[count]
        question = pb_questions.find_one({'p_id': question_id})
        answers_query = list(pb_answers.find({'id_questions': question_id}))
        a_text = ''
        for ans in answers_query:
            sort_num = ans.get('sort_number')
            text = ans.get('answer')
            a_text = f'{a_text}\n<b>{sort_num}</b>. {text}'
        q_text = question.get('text')
        await message.edit_text(
            f'<i>Вопрос №{count+1}\n</i><b>{q_text}</b>\n{a_text}',
            reply_markup=kb.variants_btns(employee, answers_query, question.get("p_id")),
            parse_mode='HTML'
        )


@router.callback_query(F.data.startswith('answer_'))
async def answer_check(call: CallbackQuery):
    _, employee, ans_id, q_id = call.data.split('_')
    ans_check = pb_answers.find_one({'p_id': int(ans_id)}).get('correct_answer')
    user_id = call.message.chat.id
    user_stats = pb_users_stats.find_one({'user_id': user_id})
    test_result = user_stats.get('test_result')
    test_result.append(ans_check)
    test_count = user_stats.get('test_question_count') + 1
    pb_users_stats.update_one(
        {'user_id': user_id},
        {'$set': {'test_result': test_result, 'test_question_count': test_count}}
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
        reply_markup=kb.question_result_menu(employee),
        parse_mode='HTML'
    )


@router.callback_query(F.data.startswith('testing_'))
async def testing_check_choice(call: CallbackQuery):
    _, employee, choice = call.data.split('_')
    user_id = call.message.chat.id
    if choice == 'exit':
        pb_users_stats.update_one(
            {'user_id': user_id},
            {'$set': {'test_result': [], 'test_question_count': 0}}
        )
        await call.message.edit_text('Тест завершён, прогресс сброшен')
    elif choice == 'next':
        await test_send_question(call.message, employee)


async def testing(message: Message, employee):
    q_num = TEST_SIZE_ITR if employee == 'itr' else TEST_SIZE_ISP
    await message.edit_text(
        f'Тестовое задание для самопроверки состоит из {q_num}-ти вопросов.',
        reply_markup=kb.test_menu(employee)
    )


@router.callback_query(F.data.startswith('test_'))
async def testing_choice(call: CallbackQuery):
    _, employee, choice = call.data.split('_')
    if choice == 'exit':
        await call.message.delete()
    elif choice == 'start':
        await get_testing_questions(call.message, employee)


async def learning(message: Message, employee):
    user_stats = pb_users_stats.find_one({'user_id': message.chat.id})
    if user_stats is None:
        pb_users_stats.insert_one(
            {'user_id': message.chat.id, 'question_itr_count': 1, 'question_isp_count': 1}
        )
        await send_learning_question(message, 1, employee)
    else:
        learn_count = user_stats.get(f'question_{employee}_count', 1)
        await message.edit_text(
            text=(f'В прошлый раз Вы остановились на вопросе #{learn_count}'),
            reply_markup=kb.learning_menu(employee),
        )


@router.callback_query(F.data.startswith('learn_'))
async def learn_choice(call: CallbackQuery):
    _, employee, choice = call.data.split('_')
    if choice == 'new':
        await send_learning_question(call.message, count=1, employee=employee)
    elif choice == 'continue':
        count = pb_users_stats.find_one({'user_id': call.message.chat.id}).get(f'question_{employee}_count', 1)
        await send_learning_question(call.message, count, employee)


async def searching(message: Message):
    await message.answer(
        text=('Введите и отправьте текст вопроса для поиска. '
              'Чем больше слов Вы введете тем точнее выполнится поиск.'),
    )
    await message.delete()
    await Searching.waiting_search_text.set()


@router.message(Searching.waiting_search_text)
async def question_search(message: Message, state: FSMContext):
    await state.finish()
    q_search = list(pb_questions.find(
        {'$text': {'$search': f'\"{message.text}\"'}}
    ))
    len_search = len(q_search)
    if len_search == 0:
        await message.answer(
            f'Вопросов с таким текстом не найдено, попробуйте ввести больше слов.',
            reply_markup=kb.search_menu()
        )
    elif len_search == 1:
        q_id = q_search[0].get('p_id')
        ans = pb_answers.find({'id_questions': q_id, 'correct_answer': 1})
        q_text = pb_questions.find_one({'p_id': q_id}).get('text')
        ans_text = ''
        for i in list(ans):
            text = i.get('answer')
            ans_id = i.get('sort_number')
            ans_text = f'{ans_text}\n{ans_id}. {text}'
        await message.answer(
            f'Вопрос: {q_text}\n\nПравильный вариант ответа: {ans_text}',
            reply_markup=kb.search_menu()
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
            ' Для уточнения результата попробуйте ввести "уникальное" сочетание слов.'
            '\nМожете скопировать Ваш запрос ниже и дополнить его.'),
            reply_markup=kb.search_menu()
        )
        await message.answer(message.text)


@router.callback_query(F.data.startswith('search_'))
async def searching_choice(call: CallbackQuery):
    _, choice = call.data.split('_')
    if choice == 'exit':
        await call.message.delete()
    elif choice == 'next':
        await searching(call.message)


@router.message(Command('rpo'))
async def pb_select(message: Message):
    # для нескольких програм обучения "p_id" нужно будет запрашивать у пользователя
    program_name = pb_program_groups.find_one({'p_id': 100000227}).get('title')
    await message.answer(
        text=f'{program_name}\n\nВыберите режим:',
        reply_markup=kb.main_menu(),
    )
    await message.delete()


@router.callback_query(F.data.startswith('rpo_'))
async def get_mode(call: CallbackQuery):
    _, employee, mode = call.data.split('_')
    if mode == 'learn':
        await learning(call.message, employee)
    elif mode == 'test':
        await testing(call.message, employee)
    elif mode == 'search':
        await searching(call.message)
