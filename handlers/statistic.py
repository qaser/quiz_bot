from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from bson.objectid import ObjectId
import pprint

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


async def user_stat(user_id):
    TEST_TRANSLATE = {
        'input': 'входной тест',
        'output': 'выходной тест'
    }
    QUARTER_TEXT = {
        1: 'первый квартал',
        2: 'второй квартал',
        3: 'третий квартал',
        4: 'четвёртый квартал',
    }
    queryset = results.find(
        {'user_id': user_id, 'test_type': {'$ne': 'special'}}
    )
    res_dict = {}
    for res in list(queryset):
        quiz_results = res.get('quiz_results')
        len_test = len(quiz_results)
        done_count = 0
        for q in quiz_results:
            if q[3] == 'true':
                done_count += 1
        if res_dict.get(res.get('year')) is None:
            res_dict[res.get('year')] = {}
        if res_dict.get(res.get('year')).get(res.get('quarter')) is None:
            res_dict[res.get('year')][res.get('quarter')] = {}
        res_dict[res.get('year')][res.get('quarter')][res.get('test_type')] = [
            res.get('grade'),
            len_test,
            done_count
        ]
    final_text = ''
    for year, quarters in res_dict.items():
        year_text = ''
        for quarter, test in quarters.items():
            quarter_text = ''
            for test_type, test_data in test.items():
                grade, len_test, done_count = test_data
                test_name = TEST_TRANSLATE.get(test_type)
                text = (f'        <i>{test_name}</i>\n'
                        f'              вопросов: {len_test}\n'
                        f'              правильно: {done_count}\n'
                        f'              результат: {grade}\n')
                quarter_text = f'{quarter_text}{text}'
            q_text = f'   <u>{QUARTER_TEXT.get(quarter)}</u>:\n{quarter_text}\n'
            year_text = f'{year_text}{q_text}'
        y_text = f'<b>{year} год</b>\n{year_text}\n'
        final_text = f'{final_text}{y_text}'
    return final_text


async def my_stats(message: types.Message):
    stat_text = await user_stat(message.from_user.id)
    await message.delete()
    await message.answer(stat_text, parse_mode=types.ParseMode.HTML)


@admin_check
async def users_stats(message:types.Message):
    department = users.find_one({'user_id': message.from_user.id}).get('department')
    users_queryset = users.find({'department': department})
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(
            text=u.get('full_name'),
            callback_data=f'userstats_{u.get("user_id")}'
        ) for u in users_queryset
    ]
    # for u in users_queryset:
    #     username = u.get('full_name')
    #     user_id = u.get('user_id')
    #     keyboard.add(
    #         types.InlineKeyboardButton(
    #             text=username,
    #             callback_data=f'userstats_{user_id}'
    #         )
    #     )
    keyboard.add(*buttons)
    keyboard.add(
        types.InlineKeyboardButton(text='< Отмена >', callback_data='exit'),
    )
    await message.delete()
    await message.answer(
        text=('Выберите пользователя для просмотра статистики:'),
        reply_markup=keyboard,
    )


@dp.callback_query_handler(Text(startswith='userstats_'))
async def send_user_stats(call: types.CallbackQuery):
    _, user_id = call.data.split('_')
    username = users.find_one({'user_id': int(user_id)}).get('full_name')
    stat_text = await user_stat(int(user_id))
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='< Выход >', callback_data='exit'))
    await call.message.delete()
    await call.message.answer(
        text=f'Статистика пользователя {username}:\n{stat_text}',
        parse_mode=types.ParseMode.HTML,
        reply_markup=keyboard
    )


def register_handlers_statistic(dp: Dispatcher):
    dp.register_message_handler(stat_now, commands='unsolve_test')
    dp.register_message_handler(my_stats, commands='my_stats')
    dp.register_message_handler(users_stats, commands='users_stats')
