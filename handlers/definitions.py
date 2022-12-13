from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from config.bot_config import bot, dp
from utils.constants import LABOR_SAFETY, RISKS, SUBSTANCES, INDUSTRIAL_SAFETY


async def values_gas(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    for word in SUBSTANCES.keys():
        keyboard.add(
            types.InlineKeyboardButton(
                text=word,
                callback_data=f'gas_{word}'
            )
        )
    await message.answer(
        'Выберите нужное Вам определение',
        reply_markup=keyboard,
    )


async def values_pb(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    for word in INDUSTRIAL_SAFETY.keys():
        keyboard.add(
            types.InlineKeyboardButton(
                text=word,
                callback_data=f'pb_{word}'
            )
        )
    await message.answer(
        'Выберите нужное Вам определение',
        reply_markup=keyboard,
    )


async def values_ot(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    for word in LABOR_SAFETY.keys():
        keyboard.add(
            types.InlineKeyboardButton(
                text=word,
                callback_data=f'ot_{word}'
            )
        )
    await message.answer(
        'Выберите нужное Вам определение',
        reply_markup=keyboard,
    )


async def values_risk(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    for word in RISKS.keys():
        keyboard.add(
            types.InlineKeyboardButton(
                text=word,
                callback_data=f'risk_{word}'
            )
        )
    await message.answer(
        'Выберите нужное Вам определение',
        reply_markup=keyboard,
    )


@dp.callback_query_handler(Text(startswith='gas_'))
async def call_gas(call: types.CallbackQuery):
    _, word = call.data.split('_')
    text = SUBSTANCES.get(word, 'Определения для этого слова нет в базе данных')
    await call.message.answer(text)


@dp.callback_query_handler(Text(startswith='risk_'))
async def call_risk(call: types.CallbackQuery):
    _, word = call.data.split('_')
    text = RISKS.get(word, 'Определения для этого слова нет в базе данных')
    await call.message.answer(text)


@dp.callback_query_handler(Text(startswith='pb_'))
async def call_pb(call: types.CallbackQuery):
    _, word = call.data.split('_')
    text = INDUSTRIAL_SAFETY.get(word, 'Определения для этого слова нет в базе данных')
    await call.message.answer(text)


@dp.callback_query_handler(Text(startswith='ot_'))
async def call_ot(call: types.CallbackQuery):
    _, word = call.data.split('_')
    text = LABOR_SAFETY.get(word, 'Определения для этого слова нет в базе данных')
    await call.message.answer(text)


def register_handlers_definitions(dp: Dispatcher):
    dp.register_message_handler(values_gas, commands='gas')
    dp.register_message_handler(values_ot, commands='ot')
    dp.register_message_handler(values_pb, commands='pb')
    dp.register_message_handler(values_risk, commands='risk')
