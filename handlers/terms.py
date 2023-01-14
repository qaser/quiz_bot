from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from config.bot_config import bot, dp
from config.mongo_config import terms
from bson.objectid import ObjectId


async def terms_request(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    pipeline = [
        {'$group': {'_id': {'theme_code': '$theme_code', 'name': '$theme'}}}
    ]
    queryset = list(terms.aggregate(pipeline=pipeline))
    for theme in queryset:
        theme_code = theme['_id']['theme_code']
        theme_name = theme['_id']['name']
        keyboard.add(
            types.InlineKeyboardButton(
                text=theme_name,
                callback_data=f'theme_{theme_code}'
            )
        )
    keyboard.add(
        types.InlineKeyboardButton(text='< Выход >', callback_data='exit'),
    )
    await message.delete()
    await message.answer(
        text=('Термины и определения.\n'
              'Выберите тему:'),
        reply_markup=keyboard,
    )


@dp.callback_query_handler(Text(startswith='theme_'))
async def get_theme(call: types.CallbackQuery):
    _, theme_code = call.data.split('_')
    keyboard = types.InlineKeyboardMarkup()
    queryset = list(terms.find({'theme_code': theme_code}))
    for term in queryset:
        term_id = term['_id']
        keyboard.add(
            types.InlineKeyboardButton(
                text=term['name'],
                callback_data=f'term_{term_id}'
            )
        )
    keyboard.row(
        types.InlineKeyboardButton(text='< Выход >', callback_data='exit'),
        types.InlineKeyboardButton(text='<< Назад', callback_data='back_theme_id'),
    )
    await call.message.edit_text(
        'Выберите термин:',
        reply_markup=keyboard,
    )


@dp.callback_query_handler(text='exit')
async def terms_exit(call: types.CallbackQuery):
    await call.message.delete()


@dp.callback_query_handler(Text(startswith='term_'))
async def show_term(call: types.CallbackQuery):
    _, term_id = call.data.split('_')
    keyboard = types.InlineKeyboardMarkup()
    text = terms.find_one({'_id': ObjectId(term_id)}).get(
        'description',
        'Определения для этого слова нет в базе данных'
    )
    keyboard.row(
        types.InlineKeyboardButton(text='< Выход >', callback_data='exit'),
        types.InlineKeyboardButton(text='< Назад >', callback_data=f'back_term_{term_id}'),
    )
    await call.message.delete()
    await call.message.answer(text, reply_markup=keyboard)


@dp.callback_query_handler(Text(startswith='back_'))
async def menu_back(call: types.CallbackQuery):
    _, level, value = call.data.split('_')
    if level == 'theme':
        await terms_request(call.message)
    elif level == 'term':
        theme_code = terms.find_one({'_id': ObjectId(value)}).get('theme_code')
        keyboard = types.InlineKeyboardMarkup()
        queryset = list(terms.find({'theme_code': theme_code}))
        for term in queryset:
            term_id = term['_id']
            keyboard.add(
                types.InlineKeyboardButton(
                    text=term['name'],
                    callback_data=f'term_{term_id}'
                )
            )
        keyboard.row(
            types.InlineKeyboardButton(text='< Выход >', callback_data='exit'),
            types.InlineKeyboardButton(text='< Назад >', callback_data='back_theme_id'),
        )
        await call.message.edit_text(
            'Выберите термин:',
            reply_markup=keyboard,
        )


async def answers_send(message: types.Message):
    await message.answer('Запрос получен, ожидайте')
    await message.answer_document(open('static/answers/Билеты-ответы машинист ТК 2023.pdf', 'rb'))
    await message.answer_document(open('static/answers/Билеты-ответы слесарь РТУ 2023.pdf', 'rb'))


def register_handlers_terms(dp: Dispatcher):
    dp.register_message_handler(terms_request, commands='terms')
    dp.register_message_handler(answers_send, commands='answers')
