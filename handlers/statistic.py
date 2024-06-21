from aiogram import F, Router
from aiogram.exceptions import AiogramError
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from bson.objectid import ObjectId

import keyboards.for_statistic as kb
from config.bot_config import bot
from config.mongo_config import buffer, results, users
from utils.decorators import admin_check
from utils.utils import calc_date, calc_test_type

router = Router()

@admin_check
@router.message(Command('unsolve_test'))
async def stat_now(message: Message):
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
        users_list = ''
        for u in undone:
            users_list = f'{users_list}\n{u.get("full_name")}'
        await message.answer(
            text=f'Текущие тесты не прошли:\n{users_list}\n\n Хотите отправить уведомления?',
            reply_markup=kb.users_menu(message.from_user.id, data.inserted_id),
        )
    await message.delete()


@router.callback_query(F.data.startswith('buffer_'))
async def send_notification(call: CallbackQuery):
    _, admin_id, buffer_id = call.data.split('_')
    users_list = buffer.find_one({'_id': ObjectId(buffer_id)}).get('users_list')
    admin = users.find_one({'user_id': int(admin_id)}).get('full_name')
    for user in users_list:
        try:
            await bot.send_message(
                chat_id = user.get('user_id'),
                text=f'{admin} напоминает о необходимости прохождения теста',
            )
        except AiogramError:
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


@router.message(Command('my_stats'))
async def my_stats(message: Message):
    stat_text = await user_stat(message.from_user.id)
    await message.delete()
    await message.answer(stat_text, parse_mode='HTML')


@admin_check
@router.message(Command('user_stats'))
async def users_stats(message: Message):
    department = users.find_one({'user_id': message.from_user.id}).get('department')
    users_queryset = users.find({'department': department})
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(
            text=u.get('full_name'),
            callback_data=f'userstats_{u.get("user_id")}'
        ) for u in users_queryset
    ]
    keyboard.add(*buttons)
    keyboard.add(
        types.InlineKeyboardButton(text='< Отмена >', callback_data='exit'),
    )
    await message.delete()
    await message.answer(
        text=('Выберите пользователя для просмотра статистики:'),
        reply_markup=keyboard,
    )


@router.callback_query(F.data.startswith('userstats_'))
async def send_user_stats(call: CallbackQuery):
    _, user_id = call.data.split('_')
    username = users.find_one({'user_id': int(user_id)}).get('full_name')
    stat_text = await user_stat(int(user_id))
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='< Закрыть >', callback_data='exit'))
    await call.message.edit_text(
        text=f'Статистика пользователя {username}:\n{stat_text}',
        parse_mode='HTML',
        reply_markup=keyboard
    )
