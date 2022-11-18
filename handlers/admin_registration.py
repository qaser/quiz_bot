from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from config.bot_config import dp, bot
from config.mongo_config import admin_requests, users
from config.telegram_config import ADMIN_TELEGRAM_ID
from texts.initial import ADMIN_REQUEST
from utils.decorators import registration_check, superuser_check


class AdminRegistration(StatesGroup):
    waiting_comment = State()
    waiting_request_confirm = State()


class AdminRequestConfirm(StatesGroup):
    waiting_request = State()
    waiting_comment = State()
    waiting_confirm = State()


# обработка команды /admin_request
@registration_check
async def admin_request(message):
    user_id = message.from_user.id
    user_is_admin = users.find_one({'user_id': user_id}).get('is_admin')
    if user_is_admin == 'true':
        await message.answer('Вы уже являетесь администратором')
    request_user = admin_requests.find_one({'user_id': user_id})
    if request_user is not None:
        await message.answer('Вы уже подали заявку, ожидайте ответа')
    else:
        await message.answer(text=ADMIN_REQUEST)
        await AdminRegistration.waiting_comment.set()


async def request_confirm(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await message.answer(
            'Вы отменили подачу заявки на права Администратора'
        )
        await state.reset_state()
    else:
        await state.update_data(comment=message.text)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Нет', 'Да')
        await message.answer(
            text=f'Комментарий принят. Отправить запрос?',
            reply_markup=keyboard,
        )
        await AdminRegistration.waiting_request_confirm.set()


async def request_save(message: types.Message, state: FSMContext):
    if message.text.lower() not in ['нет', 'да']:
        await message.answer('Пожалуйста, отправьте "Да" или "Нет"')
        return
    if message.text.lower() == 'да':
        user_id = message.from_user.id
        data = await state.get_data()
        comment = data['comment']
        user = users.find_one({'user_id': user_id})
        user_dep = user.get('department')
        username = user.get('full_name')
        admin_requests.insert_one(
            {
                'user_id': user_id,
                'username': username,
                'comment': comment,
            }
        )
        await state.reset_state()
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                text='Принять',
                callback_data=f'admin_{user_id}_accept'
            )
        )
        keyboard.add(
            types.InlineKeyboardButton(
                text='Отклонить',
                callback_data=f'admin_{user_id}_deny'
            )
        )
        await bot.send_message(
            chat_id=ADMIN_TELEGRAM_ID,
            text=(
                'Получена заявка на получение прав Администратора:\n\n'
                f'{username}\n{user_dep}\n"{comment}"\n\n'
            ),
            reply_markup=keyboard
        )
        await message.answer(
            'Заявка отправлена.\nВ ближайшее время Вам придёт ответ',
            reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            ('Заявка не отправлена.\n'
             'Если необходимо отправить новую заявку '
             '- нажмите /admin_request'),
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.reset_state()


@dp.callback_query_handler(Text(startswith="admin_"))
async def admin_request_confirm(call: types.CallbackQuery):
    _, user_id, result = call.data.split('_')
    if result == 'deny':
        await bot.send_message(chat_id=user_id, text='Ваша заявка отклонена')
    else:
        users.update_one(
            {'user_id': int(user_id)},
            {'$set': {'is_admin': 'true'}},
            upsert=False
        )
        await bot.send_message(
            chat_id=user_id,
            text='Ваша заявка принята.\nВам доступны команды администратора'
        )
    await call.message.delete_reply_markup()
    admin_requests.delete_one({'user_id': int(user_id)})


def register_handlers_admin_registration(dp: Dispatcher):
    dp.register_message_handler(admin_request, commands='admin_request')
    dp.register_message_handler(
        request_confirm,
        state=AdminRegistration.waiting_comment,
    )
    dp.register_message_handler(
        request_save,
        state=AdminRegistration.waiting_request_confirm,
    )
