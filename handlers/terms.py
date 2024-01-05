from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from bson.objectid import ObjectId

from config.mongo_config import terms
import keyboards.for_terms as kb


router = Router()


@router.message(Command('terms'))
async def terms_request(message: Message):
    pipeline = [
        {'$group': {'_id': {'theme_code': '$theme_code', 'name': '$theme'}}}
    ]
    queryset = list(terms.aggregate(pipeline=pipeline))
    await message.delete()
    await message.answer(
        text='Термины и определения.\nВыберите тему:',
        reply_markup=kb.main_menu(queryset),
    )


@router.callback_query(F.data.startswith('theme_'))
async def get_theme(call: CallbackQuery):
    _, theme_code = call.data.split('_')
    queryset = list(terms.find({'theme_code': theme_code}))
    await call.message.edit_text(
        'Выберите термин:',
        reply_markup=kb.theme_menu(queryset),
    )


@router.callback_query(F.data.startswith('exit'))
async def terms_exit(call: CallbackQuery):
    await call.message.delete()


@router.callback_query(F.data.startswith('term_'))
async def show_term(call: CallbackQuery):
    _, term_id = call.data.split('_')
    text = terms.find_one({'_id': ObjectId(term_id)}).get(
        'description',
        'Определения для этого слова нет в базе данных'
    )
    await call.message.delete()
    await call.message.answer(text, reply_markup=kb.term_menu(term_id))


@router.callback_query(F.data.startswith('back_'))
async def menu_back(call: CallbackQuery):
    _, level, value = call.data.split('_')
    if level == 'theme':
        await terms_request(call.message)
    elif level == 'term':
        theme_code = terms.find_one({'_id': ObjectId(value)}).get('theme_code')
        queryset = list(terms.find({'theme_code': theme_code}))
        await call.message.edit_text(
            'Выберите термин:',
            reply_markup=kb.theme_menu(queryset),
        )
