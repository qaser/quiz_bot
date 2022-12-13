from aiogram import types
from aiogram.utils.exceptions import CantInitiateConversation

from config.bot_config import bot
from config.mongo_config import plans, questions, users
from config.telegram_config import ADMIN_TELEGRAM_ID
from utils.constants import TEST_TYPE
from utils.utils import calc_date, calc_test_type


# формирование списка вопросов согласно тем плана
async def add_questions_in_plan():
    year, _, quarter = calc_date()
    plans_queryset = list(plans.find({'year': year, 'quarter': quarter}))
    for plan in plans_queryset:
        themes = plan.get('themes')
        res = []
        for theme in themes:
            list_questions = list(questions.aggregate(
                [{'$match': {'theme': theme}}, {'$sample': {'size': 10}}]
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
    for dep in departments:
        ids = [user.get('user_id') for user in list(
            users.find({'department': dep})
        )]
        user_ids += ids
    for user_id in user_ids:
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
        except CantInitiateConversation:
            missed_user = users.find_one({'user_id': user_id}).get('full_name')
            await bot.send_message(
                ADMIN_TELEGRAM_ID,
                f'Пользователь {missed_user} не доступен',
            )
