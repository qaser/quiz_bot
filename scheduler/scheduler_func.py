import datetime as dt

from aiogram import types
from aiogram.exceptions import AiogramError
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config.bot_config import bot
from config.mongo_config import plans, users, scheduler_tu
from config.telegram_config import ADMIN_TELEGRAM_ID, CHAT_56_ID, QUIZ_THREAD_ID
from utils.constants import TEST_TYPE, TU, QUIZ_HELLO_TEXT
from utils.utils import calc_date, calc_test_type


NEWS = ('Вышло обновление бота "Проверка знаний"!\n\n'
        '1. Теперь пользователь может сам настроить викторину (тест) выбирая тематику вопросов.\n'
        'По результатам прохождения тестов у пользователя формируется Рейтинг среди других пользователей.\n'
        'Пользователь может посмотреть только СВОЙ рейтинг. Рейтинг других пользователей недоступен для просмотра.\n'
        'Чтобы рейтинг пользователя был учтён приложением необходимо пройти минимум две викторины (теста)\n'
        '2. Приложение может рекомендовать пользователю учебный материал в зависимости от результатов прохождения викторин (тестов)\n'
        '3. Пользователь может удалить свой аккаунт в любое время.\n\n'
        'Удачи!')


async def check_tu_events():
    today = dt.datetime.today().strftime('%d.%m.%Y')
    queryset = scheduler_tu.find({'date': today})
    if queryset is not None:
        for event in len(queryset):
            if event['type'] == 'quiz':
                print('Отсылаем кнопку тестирования')
            elif event['type'] == 'article':
                print('Отсылаем статью')

async def send_news():
    qs = list(users.find({}))
    for user in qs:
        await bot.send_message(
            chat_id=user['user_id'],
            text=NEWS
        )



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
                callback_data=(f'quiz_{year}_{quarter}_{test_type}')
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
    if date_now in TU.keys():
        await bot.send_message(
            chat_id=CHAT_56_ID,
            message_thread_id=QUIZ_THREAD_ID,
            text=TU.get(date_now),
            protect_content=True,
        )
