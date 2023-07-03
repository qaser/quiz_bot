import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

from config.bot_config import dp, bot
from config.mongo_config import users
from config.telegram_config import PASSWORD
from handlers.admin_registration import register_handlers_admin_registration
from handlers.attentions import register_handlers_attentions
from handlers.examen import register_handlers_examen
from handlers.import_questions import register_handlers_excel
from handlers.key_rules import register_handlers_key_rules
from handlers.pb import register_handlers_pb
from handlers.plan import register_handlers_plan
from handlers.quiz import register_handlers_quiz
from handlers.registration import register_handlers_registration
from handlers.reports import register_handlers_reports
from handlers.service import register_handlers_service
from handlers.statistic import register_handlers_statistic
from handlers.terms import register_handlers_terms
from handlers.videos import register_handlers_videos
from scheduler.scheduler_jobs import scheduler, scheduler_jobs
from texts.initial import INITIAL_TEXT

logging.basicConfig(
    filename='logs_bot.log',
    level=logging.INFO,
    filemode='a',
    format='%(asctime)s - %(message)s',
    datefmt='%d.%m.%y %H:%M:%S',
    encoding='utf-8',
)


class PasswordCheck(StatesGroup):
    waiting_password = State()


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    check_user = users.find_one({'user_id': user_id})
    if check_user is not None:
        await message.answer(INITIAL_TEXT)
    else:
        await message.answer('Введите пароль')
        await PasswordCheck.waiting_password.set()


@dp.message_handler(state=PasswordCheck.waiting_password)
async def check_password(message: types.Message, state: FSMContext):
    if message.text == PASSWORD:
        await message.answer(INITIAL_TEXT)
        await state.reset_state()
        await state.reset_data()
    else:
        await message.answer('Пароль неверный, повторите попытку')
        return


async def on_startup(_):
    scheduler_jobs()


if __name__ == '__main__':
    scheduler.start()
    register_handlers_service(dp)
    register_handlers_registration(dp)
    register_handlers_admin_registration(dp)
    register_handlers_plan(dp)
    register_handlers_quiz(dp)
    register_handlers_excel(dp)
    register_handlers_reports(dp)
    register_handlers_key_rules(dp)
    register_handlers_attentions(dp)
    register_handlers_statistic(dp)
    register_handlers_examen(dp)
    register_handlers_pb(dp)
    register_handlers_videos(dp)
    register_handlers_terms(dp)  # всегда должен быть последним
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
