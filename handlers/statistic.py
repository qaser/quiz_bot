from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from bson.objectid import ObjectId

from config.bot_config import bot, dp
from config.mongo_config import buffer, results, users
from utils.decorators import admin_check
from utils.utils import calc_date, calc_test_type
from aiogram.utils.exceptions import CantInitiateConversation


@admin_check
async def stat_now(message: types.Message):
    department = users.find_one({'user_id': message.from_user.id}).get('department')
    dep_users = list(users.find({'department': department}))
    year, month, quarter = calc_date()
    test_type = calc_test_type(month)
    queryset = list(results.find(
        {
            'year': year,
            'quarter': quarter,
            'test_type': test_type,
            'done': 'true'
        }
    ))
    done = []
    undone = []
    for user in dep_users:
        user_id = user.get('user_id')
        for res in queryset:
            if user_id == res.get('user_id'):
                done.append(user.get('user_id'))
        if user_id not in done:
            undone.append(user)
    if len(undone) == 0:
        await message.answer(f'Текущие тесты прошли все пользователи')
    else:
        data = buffer.insert_one({'users_list': undone})
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                text='Отправить',
                callback_data=f'buffer_{message.from_user.id}_{data.inserted_id}'
            ),
        )
        keyboard.add(
            types.InlineKeyboardButton(
                text='Отмена',
                callback_data=f'exit'
            ),
        )
        users_list = ''
        for u in undone:
            users_list = f'{users_list}\n{u.get("full_name")}'
        await message.answer(
            text=f'Текущие тесты не прошли:\n{users_list}\n\n Хотите отправить уведомления?',
            reply_markup=keyboard,
        )
    await message.delete()


@dp.callback_query_handler(Text(startswith='buffer_'))
async def send_notification(call: types.CallbackQuery):
    _, admin_id, buffer_id = call.data.split('_')
    users_list = buffer.find_one({'_id': ObjectId(buffer_id)}).get('users_list')
    admin = users.find_one({'user_id': int(admin_id)}).get('full_name')
    for user in users_list:
        try:
            await bot.send_message(
                chat_id = user.get('user_id'),
                text=f'{admin} напоминает о необходимости прохождения теста',
            )
        except CantInitiateConversation:
                await bot.send_message(
                    chat_id=admin,
                    text=f'Пользователь {user.get("full_name")} вероятно заблокировал бота.'
                )
                continue
    await call.message.edit_text('Сообщения отправлены')
    await call.message.delete_reply_markup()


def register_handlers_statistic(dp: Dispatcher):
    dp.register_message_handler(stat_now, commands='unsolve_test')
