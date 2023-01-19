from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from config.bot_config import bot, dp
from config.mongo_config import terms
from bson.objectid import ObjectId
from utils.constants import EXAMEN
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext


class Menu(StatesGroup):
    menu_step = State()


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


@dp.message_handler(state=Menu.menu_step)
@dp.callback_query_handler(Text(startswith='examen_'))
async def get_profession(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(step='prof')
    _, profession = call.data.split('_')
    keyboard = types.InlineKeyboardMarkup()
    for ticket in EXAMEN.get(profession).keys():
        keyboard.add(
            types.InlineKeyboardButton(
                text=ticket,
                callback_data=f'ticket_{ticket}'
            )
        )
    keyboard.row(
        types.InlineKeyboardButton(text='< Выход >', callback_data='exit'),
        types.InlineKeyboardButton(text='<< Назад', callback_data='back_prof'),
    )
    await call.message.edit_text(
        'Выберите билет:',
        reply_markup=keyboard,
    )


def register_handlers_examen(dp: Dispatcher):
    dp.register_message_handler(examen_request, commands='examen')
