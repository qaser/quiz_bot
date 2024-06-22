import datetime as dt

from aiogram.exceptions import AiogramError
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config.bot_config import bot
from config.mongo_config import plans, scheduler_tu, users
from config.telegram_config import (ADMIN_TELEGRAM_ID, CHAT_56_ID,
                                    QUIZ_THREAD_ID)
from utils.constants import NEXT_BUTTON, TEST_TYPE, TU

NEWS = ('Удачи!')


async def check_tu_events():
    today = dt.datetime.today().strftime('%d.%m.%Y')
    queryset = scheduler_tu.find({'date': today})
    if queryset is not None:
        for event in list(queryset):
            if event['type'] == 'quiz_plan':
                plan_id = event['event_id']
                tu_event = plans.find_one({'_id': plan_id})
                q = tu_event['quarter']
                y = tu_event['year']
                quiz_type = TEST_TYPE[event['quiz_type']]
                target_users = list(users.find({'department': tu_event['department']}))
                target_admins = list(users.find(
                    {'department': tu_event['department'], 'is_admin': True}
                ))
                for user in target_users:
                    user_id = user['user_id']
                    kb = InlineKeyboardBuilder()
                    kb.button(
                        text=NEXT_BUTTON,
                        callback_data=f'tu_{str(plan_id)}_{event["quiz_type"]}'
                    )
                    try:
                        await bot.send_message(
                            chat_id=user_id,
                            text=(f'Пройдите {quiz_type} тест знаний по '
                                  f'плану технической учебы за {q} кв. {y} г.'),
                            reply_markup=kb.as_markup(),
                            protect_content=True
                        )
                    except AiogramError:
                        for admin_user in target_admins:
                            try:
                                await bot.send_message(
                                    admin_user['user_id'],
                                    f'Пользователь с id {user["user_id"]} недоступен',
                                )
                            except AiogramError:
                                await bot.send_message(
                                    ADMIN_TELEGRAM_ID,
                                    f'Администратор {user} недоступен',
                                )
            elif event['type'] == 'article_plan':
                print('Отсылаем статью')


async def send_news():
    qs = list(users.find({}))
    count = 0
    for user in qs:
        try:
            await bot.send_message(
                chat_id=user['user_id'],
                text=NEWS
            )
            count += 1
        except:
            pass
    await bot.send_message(
        ADMIN_TELEGRAM_ID,
        text=f'Рассылка отправлена. Доступно {count} из {len(qs)}'
    )



# # отправка кнопки для начала тестирования
# async def send_quiz_button():
#     year, month, quarter = calc_date()
#     test_type = calc_test_type(month)
#     test_type_name = TEST_TYPE.get(test_type)
#     queryset = list(plans.find({'year': year, 'quarter': quarter}))
#     departments = [dep.get('department') for dep in queryset]
#     user_ids = []
#     for dep in departments:
#         ids = [user.get('user_id') for user in list(users.find({'department': dep}))]
#         user_ids += ids
#     for user_id in user_ids:
#         target_user = users.find_one({'user_id': user_id}).get('full_name')
#         try:
#             kb = InlineKeyboardBuilder()
#             kb.button(
#                 text='Начать тестирование',
#                 callback_data=(f'quiz_{year}_{quarter}_{test_type}')
#             )
#             await bot.send_message(
#                 chat_id=user_id,
#                 text=(
#                     f'Пройдите {test_type_name} тест знаний по '
#                     f'плану технической учёбы {quarter}-го квартала.'
#                 ),
#                 reply_markup=kb.as_markup(),
#             )
#             await bot.send_message(
#                 ADMIN_TELEGRAM_ID,
#                 f'Пользователю {target_user} отправлен тест',
#             )
#         except AiogramError:
#             await bot.send_message(
#                 ADMIN_TELEGRAM_ID,
#                 f'Пользователь {target_user} не доступен',
#             )


# # отправка кнопки для начала тестирования в чат
# async def send_quiz_button_in_chat():
#     year, month, quarter = calc_date()
#     test_type = calc_test_type(month)
#     test_type_name = TEST_TYPE.get(test_type)
#     kb = InlineKeyboardBuilder()
#     kb.button(
#         text='Начать тестирование',
#         callback_data=(f'quiz_{year}_{quarter}_{test_type}')
#     )
#     await bot.send_message(
#         chat_id=CHAT_56_ID,
#         message_thread_id=QUIZ_THREAD_ID,
#         text=(
#             f'Пройдите <u>{test_type_name}</u> тест знаний по '
#             f'плану технической учёбы <u>{quarter}-го квартала</u>.\n'
#             f'{QUIZ_HELLO_TEXT}'
#         ),
#         protect_content=True,
#         reply_markup=kb.as_markup(),
#         parse_mode='HTML'
#     )


async def send_tu_material():
    date_now = dt.datetime.now().strftime('%d.%m.%Y')
    if date_now in TU.keys():
        await bot.send_message(
            chat_id=CHAT_56_ID,
            message_thread_id=QUIZ_THREAD_ID,
            text=TU.get(date_now),
            protect_content=True,
        )
