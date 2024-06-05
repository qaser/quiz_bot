import datetime as dt
from aiogram import Router, F

from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config.bot_config import dp
from config.mongo_config import users, conditions
from aiogram.utils.keyboard import InlineKeyboardBuilder


DISCLAIMER = 'Для продолжения работы с сервисом Вам необходимо принять "Пользовательское соглашение"'
START_TEXT = 'В нижней части есть кнопка "Меню", там Вы найдете всё необходимое'

router = Router()


@dp.message(Command('start'))
async def cmd_start(message: Message):
    user = message.from_user
    check_user_agree = users.find_one({'user_id': user.id, 'conditions_agree': True})
    check_user_not_agree = users.find_one({'user_id': user.id, 'conditions_agree': False})
    if check_user_agree:
        await message.answer(START_TEXT)
    elif check_user_not_agree:
        await show_conditions(message)
    else:
        users.insert_one(
            {
                'user_id': user.id,
                'is_admin': False,
                'is_superuser': False,
                'is_premium': False,
                'silent_mode': False,
                'conditions_agree': False,
                'reg_date': dt.datetime.now()
            }
        )
        await show_conditions(message)


async def show_conditions(message):
    kb = InlineKeyboardBuilder()
    kb.button(text='Принять', callback_data=f'cond_accept')
    kb.button(text='Отклонить', callback_data=f'cond_decline')
    kb.adjust(1)
    condition = conditions.find({}).sort({'release_date': -1}).limit(1)[0]
    text = condition['text']
    await message.answer(
        f'Пользовательское соглашение:\n{text}',
        reply_markup=kb.as_markup(),
        parse_mode='HTML'
    )
    await message.delete()


@router.callback_query(F.data.startswith('cond_'))
async def send_notification(call: CallbackQuery, state: FSMContext):
    _, answer = call.data.split('_')
    user_id = call.message.chat.id
    if answer == 'accept':
        users.update_one(
            {'user_id': user_id},
            {'$set': {'conditions_agree': True}}
        )
        await call.message.answer(START_TEXT)
    else:
        users.delete_one({'user_id': user_id})
        await call.message.answer(f'{DISCLAIMER}. Нажмите /start')
    await state.clear()
    await call.message.delete()
