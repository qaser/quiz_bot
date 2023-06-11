import datetime as dt

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import CantInitiateConversation

from config.bot_config import bot, dp
from config.mongo_config import (pb_answers, pb_instruction_sections, pb_link,
                                 pb_nd, pb_nd_documents, pb_program_groups,
                                 pb_questions, pb_users_stats, pb_programs, users, pb_rpo_program)
from config.telegram_config import ADMIN_TELEGRAM_ID
from scheduler.scheduler_func import send_quiz_button
from utils.utils import calc_grade, word_conjugate


def get_learning_question(count):
    q_id = pb_rpo_program.find_one({'count': count}).get('id_question')
    q_text = pb_questions.find_one({'p_id': q_id}).get('text')
    a_text = pb_answers.find_one({'id_questions': q_id, 'correct_answer': 1}).get('answer')
    return f'Вопрос №{count} из 2243\n\n<b>{q_text}</b>\n\n{a_text}'


async def send_learning_question(message:types.Message, count):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(text='Завершить', callback_data=f'learning_finish_{count}'),
        types.InlineKeyboardButton(text='Следующий', callback_data=f'learning_next_{count+1}'),
    )
    pb_users_stats.update_one(
        {'user_id': message.from_user.id},
        {'$set': {'question_count': count}}
    )
    text = get_learning_question(count)
    await message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode=types.ParseMode.HTML
    )


@dp.callback_query_handler(Text(startswith='learning_'))
async def learning_choice(call: types.CallbackQuery):
    _, choice, count = call.data.split('_')
    if choice == 'finish':
        pb_users_stats.update_one(
            {'user_id': call.message.from_user.id},
            {'$set': {'question_count': int(count)}}
        )
        await call.message.delete()
    elif choice == 'next':
        text = get_learning_question(int(count)+1)
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(text='Завершить', callback_data=f'learning_finish_{count}'),
            types.InlineKeyboardButton(text='Следующий', callback_data=f'learning_next_{int(count)+1}'),
        )
        await call.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode=types.ParseMode.HTML
        )



async def learning(message: types.Message):
    user_stats = pb_users_stats.find_one({'user_id': message.from_user.id})
    if user_stats is None:
        pb_users_stats.insert_one(
            {'user_id': message.from_user.id, 'question_count': 1}
        )
        await message.delete()
        await send_learning_question(message, 1)
    else:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(text='Начать заново', callback_data='learn_new'),
            types.InlineKeyboardButton(text='Продолжить', callback_data='learn_continue'),
        )
        learn_count = user_stats.get('question_count')
        await message.edit_text(
            text=(f'В прошлый раз Вы остановились на вопросе #{learn_count}'),
            reply_markup=keyboard,
        )


@dp.callback_query_handler(Text(startswith='learn_'))
async def learn_choice(call: types.CallbackQuery):
    _, choice = call.data.split('_')
    if choice == 'new':
        await send_learning_question(call.message, count=1)
    elif choice == 'continue':
        count = pb_users_stats.find_one({'user_id': call.message.from_user.id}).get('question_count')
        await send_learning_question(call.message, count)


async def pb_select(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(text='Обучение', callback_data='rpo_learn'),
        types.InlineKeyboardButton(text='Самопроверка', callback_data='rpo_test'),
    )
    # для нескольких програм обучения "p_id" нужно будет запрашивать у пользователя
    program_name = pb_program_groups.find_one({'p_id': 100000227}).get('title')
    await message.answer(
        text=(f'{program_name}\n\n'
              'Выберите режим:'),
        reply_markup=keyboard,
    )
    await message.delete()


@dp.callback_query_handler(Text(startswith='rpo_'))
async def get_mode(call: types.CallbackQuery):
    _, mode = call.data.split('_')
    if mode == 'learn':
        await learning(call.message)
    elif mode == 'test':
        await call.message.answer('Режим "Самопроверка" в разработке. Выберите режим "Обучение"\n\n/rpo')
        await call.message.delete()



def register_handlers_pb(dp: Dispatcher):
    dp.register_message_handler(pb_select, commands='rpo')
