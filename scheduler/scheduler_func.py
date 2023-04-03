import datetime as dt

from aiogram import types
from aiogram.utils.exceptions import CantInitiateConversation, BotBlocked

from config.bot_config import bot
from config.mongo_config import plans, questions, users
from config.telegram_config import ADMIN_TELEGRAM_ID
from utils.constants import TEST_TYPE, TU
from utils.utils import calc_date, calc_test_type


# формирование списка вопросов согласно тем плана
async def add_questions_in_plan():
    year, _, quarter = calc_date()
    plans_queryset = list(plans.find({'year': year, 'quarter': quarter}))
    for plan in plans_queryset:
        themes = plan.get('themes')
        res = []
        num_themes = len(themes)
        num_q = 30 // num_themes
        for theme in themes:
            list_questions = list(questions.aggregate(
                [{'$match': {'theme': theme}}, {'$sample': {'size': num_q}}]
            ))
            q_ids = [q.get('_id') for q in list_questions]
            res = res + q_ids
        plans.update_one(
            {'_id': plan.get('_id')},
            {'$set': {'questions': res}}
        )
    await bot.send_message(ADMIN_TELEGRAM_ID, 'Тесты сформированы')


# отправка кнопки для начала тестирования
async def send_quiz_button():
    year, month, quarter = calc_date()
    test_type = calc_test_type(month)
    test_type_name = TEST_TYPE.get(test_type)
    queryset = list(plans.find({'year': year, 'quarter': quarter}))
    departments = [dep.get('department') for dep in queryset]
    user_ids = []
    pass_user_ids = [  # убрать эту строку
        440028496,
        5303483860,
        1078523396,
        5079055032,
        5446742270,
        480818965,
        935436102
    ]
    for dep in departments:
        ids = [user.get('user_id') for user in list(
            users.find({'department': dep})
        )]
        user_ids += ids
    for user_id in user_ids:
        if user_id not in pass_user_ids:  # убрать эту строчку
            target_user = users.find_one({'user_id': user_id}).get('full_name')
            try:
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(
                    types.InlineKeyboardButton(
                        text='Начать тестирование',
                        callback_data=(
                            f'quiz_{year}_{quarter}_{test_type}_{user_id}'
                        )
                    )
                )
                await bot.send_message(
                    chat_id=user_id,
                    text=(
                        f'Пройдите {test_type_name} тест знаний по '
                        f'плану технической учёбы {quarter}-го квартала.'
                    ),
                    reply_markup=keyboard,
                )
                await bot.send_message(
                    ADMIN_TELEGRAM_ID,
                    f'Пользователю {target_user} отправлен тест',
                )
            except (CantInitiateConversation, BotBlocked):
                await bot.send_message(
                    ADMIN_TELEGRAM_ID,
                    f'Пользователь {target_user} не доступен',
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
