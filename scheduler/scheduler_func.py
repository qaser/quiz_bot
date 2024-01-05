import datetime as dt

from aiogram import types
from aiogram.exceptions import AiogramError
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config.bot_config import bot
from config.mongo_config import plans, users
from config.telegram_config import ADMIN_TELEGRAM_ID, CHAT_56_ID, QUIZ_THREAD_ID
from utils.constants import TEST_TYPE, TU, QUIZ_HELLO_TEXT
from utils.utils import calc_date, calc_test_type


# отправка кнопки для начала тестирования
async def send_quiz_button():
    year, month, quarter = calc_date()
    test_type = calc_test_type(month)
    test_type_name = TEST_TYPE.get(test_type)
    queryset = list(plans.find({'year': year, 'quarter': quarter}))
    departments = [dep.get('department') for dep in queryset]
    user_ids = []
    for dep in departments:
        ids = [user.get('user_id') for user in list(users.find({'department': dep}))]
        user_ids += ids
    for user_id in user_ids:
        target_user = users.find_one({'user_id': user_id}).get('full_name')
        try:
            kb = InlineKeyboardBuilder()
            kb.button(
                text='Начать тестирование',
                callback_data=(f'quiz_{year}_{quarter}_{test_type}_{user_id}')
            )
            await bot.send_message(
                chat_id=user_id,
                text=(
                    f'Пройдите {test_type_name} тест знаний по '
                    f'плану технической учёбы {quarter}-го квартала.'
                ),
                reply_markup=kb.as_markup(),
            )
            await bot.send_message(
                ADMIN_TELEGRAM_ID,
                f'Пользователю {target_user} отправлен тест',
            )
        except AiogramError:
            await bot.send_message(
                ADMIN_TELEGRAM_ID,
                f'Пользователь {target_user} не доступен',
            )


# отправка кнопки для начала тестирования в чат
async def send_quiz_button_in_chat():
    year, month, quarter = calc_date()
    test_type = calc_test_type(month)
    test_type_name = TEST_TYPE.get(test_type)
    kb = InlineKeyboardBuilder()
    kb.button(
        text='Начать тестирование',
        callback_data=(f'quiz_{year}_{quarter}_{test_type}')
    )
    await bot.send_message(
        chat_id=CHAT_56_ID,
        message_thread_id=QUIZ_THREAD_ID,
        text=(
            f'Пройдите <u>{test_type_name}</u> тест знаний по '
            f'плану технической учёбы <u>{quarter}-го квартала</u>.\n'
            f'{QUIZ_HELLO_TEXT}'
        ),
        protect_content=True,
        reply_markup=kb.as_markup(),
        parse_mode='HTML'
    )


async def send_tu_material():
    date_now = dt.datetime.now().strftime('%d.%m.%Y')
    users_ids = list(users.find({}))
    if date_now in TU.keys():
        for id in users_ids:
            await bot.send_message(
                id.get('user_id'),
                TU.get(date_now),
            )
