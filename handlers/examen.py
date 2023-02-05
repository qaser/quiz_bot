from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from bson.objectid import ObjectId

from config.bot_config import bot, dp
from config.mongo_config import terms
from utils.constants import EXAMEN


async def examen_request(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    for prof in EXAMEN.keys():
        keyboard.add(
            types.InlineKeyboardButton(
                text=prof,
                callback_data=f'examen_{prof}'
            )
        )
    keyboard.add(
        types.InlineKeyboardButton(text='< Выход >', callback_data='exit'),
    )
    await message.delete()
    await message.answer(
        text=('Ответы на билеты экзамена\n'
              'Выберите профессию:'),
        reply_markup=keyboard,
    )


@dp.callback_query_handler(Text(startswith='examen_'))
async def get_profession(call: types.CallbackQuery, state: FSMContext):
    _, profession = call.data.split('_')
    keyboard = types.InlineKeyboardMarkup()
    for ticket in EXAMEN.get(profession).keys():
        keyboard.add(
            types.InlineKeyboardButton(
                text=ticket,
                callback_data=f'ticket_{profession}_{ticket}'
            )
        )
    keyboard.row(
        types.InlineKeyboardButton(text='< Выход >', callback_data='exit'),
    )
    await call.message.edit_text(
        f'Вы выбрали профессию "{profession}"\n\nВыберите билет:',
        reply_markup=keyboard,
    )


@dp.callback_query_handler(Text(startswith='ticket_'))
async def get_ticket(call: types.CallbackQuery, state: FSMContext):
    _, profession, ticket = call.data.split('_')
    keyboard = types.InlineKeyboardMarkup()
    for question in EXAMEN.get(profession).get(ticket):
        keyboard.add(
            types.InlineKeyboardButton(
                text=question,
                callback_data=f'question_{profession}_{ticket}_{question}'
            )
        )
    keyboard.row(
        types.InlineKeyboardButton(text='< Выход >', callback_data='exit'),
        types.InlineKeyboardButton(text='<< Назад', callback_data=f'examen_{profession}'),
    )
    await call.message.edit_text(
        f'Вы выбрали профессию "{profession}", {ticket}\n\nВыберите вопрос:',
        reply_markup=keyboard,
    )


@dp.callback_query_handler(Text(startswith='question_'))
async def get_question(call: types.CallbackQuery, state: FSMContext):
    _, profession, ticket, question = call.data.split('_')
    keyboard = types.InlineKeyboardMarkup()
    # keyboard.add(
    #     types.InlineKeyboardButton(
    #         text=EXAMEN.get(profession).get(ticket).get(question),
    #         # url=EXAMEN.get(profession).get(ticket).get(question),
    #         callback_data=f'answer_{profession}_{ticket}_{question}'
    #     )
    # )
    url_text = EXAMEN.get(profession).get(ticket).get(question)
    keyboard.row(
        types.InlineKeyboardButton(text='< Выход >', callback_data='exit'),
        types.InlineKeyboardButton(text='<< Назад', callback_data=f'ticket_{profession}_{ticket}'),
    )
    await call.message.edit_text(
        f'Ответ на {question}, {ticket}, профессия "{profession}"\n\n{url_text}',
        reply_markup=keyboard,
    )


def register_handlers_examen(dp: Dispatcher):
    dp.register_message_handler(examen_request, commands='answers')
