from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

import keyboards.for_admin_registration as kb
from config.bot_config import bot
from config.mongo_config import admin_requests, users
from config.telegram_config import ADMIN_TELEGRAM_ID
from utils.decorators import registration_check

ADMIN_REQUEST = (
    'Вы собираетесь подать заявку на права Администратора '
    'системы.\n\n'
    'Напишите комментарий, который поможет определить '
    'целесообразность предоставления Вам этих прав.\n'
    'Если Вы передумали, то введите "отмена"'
)


router = Router()


class AdminRegistration(StatesGroup):
    waiting_comment = State()
    waiting_request_confirm = State()


class AdminRequestConfirm(StatesGroup):
    waiting_request = State()
    waiting_comment = State()
    waiting_confirm = State()


@registration_check
@router.message(Command('admin'))
async def admin_request(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_is_admin = users.find_one({'user_id': user_id}).get('is_admin')
    if user_is_admin == True:
        await message.answer('Вы уже являетесь администратором')
    else:
        request_user = admin_requests.find_one({'user_id': user_id})
        if request_user is not None:
            await message.answer('Вы уже подали заявку, ожидайте ответа')
        else:
            await message.answer(text=ADMIN_REQUEST)
            await state.set_state(AdminRegistration.waiting_comment)


@router.message(AdminRegistration.waiting_comment)
async def request_confirm(message: Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await message.answer(
            'Вы отменили подачу заявки на права Администратора'
        )
        await state.clear()
    else:
        await state.update_data(comment=message.text)
        await message.answer(
            text='Комментарий принят. Отправить запрос?',
            reply_markup=kb.get_yes_no_kb(),
        )
        await state.set_state(AdminRegistration.waiting_request_confirm)


@router.message(AdminRegistration.waiting_request_confirm)
async def request_save(message: Message, state: FSMContext):
    if message.text.lower() not in ['нет', 'да']:
        await message.answer('Пожалуйста, отправьте "Да" или "Нет"')
        return
    if message.text.lower() == 'да':
        user_id = message.from_user.id
        data = await state.get_data()
        comment = data['comment']
        username = message.from_user.full_name
        admin_requests.insert_one(
            {
                'user_id': user_id,
                'username': message.from_user.full_name,
                'comment': comment,
            }
        )
        await state.clear()
        await bot.send_message(
            chat_id=ADMIN_TELEGRAM_ID,
            text=(
                'Получена заявка на получение прав Администратора:\n\n'
                f'{username}\n"{comment}"\n\n'
            ),
            reply_markup=kb.accept_or_deny(user_id)
        )
        await message.answer(
            'Заявка отправлена.\nВ ближайшее время Вам придёт ответ',
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            ('Заявка не отправлена.\n'
             'Если необходимо отправить новую заявку '
             '- нажмите /admin_request'),
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()


@router.callback_query(F.data.startswith('admin_'))
async def admin_request_confirm(call: CallbackQuery):
    _, user_id, result = call.data.split('_')
    if result == 'deny':
        await bot.send_message(
            chat_id=user_id,
            text='Ваша заявка на права администратора отклонена'
        )
    else:
        users.update_one(
            {'user_id': int(user_id)},
            {'$set': {'is_admin': True}},
            upsert=False
        )
        await bot.send_message(
            chat_id=user_id,
            text='Ваша заявка принята.\nВам доступны команды администратора'
        )
    await call.message.delete_reply_markup()
    admin_requests.delete_one({'user_id': int(user_id)})
