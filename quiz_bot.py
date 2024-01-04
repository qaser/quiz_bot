import asyncio
import logging

from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config.bot_config import dp, bot
from config.mongo_config import users
from config.telegram_config import PASSWORD
from handlers import (admin_registration, key_rules, pb, plan,
                      quiz, registration, reports, service, statistic, terms, videos)
from texts.initial import INITIAL_TEXT
from scheduler.scheduler_func import send_quiz_button, send_quiz_button_in_chat
import utils.constants as const


logging.basicConfig(
    filename='logs_bot.log',
    level=logging.INFO,
    filemode='a',
    format='%(asctime)s - %(message)s',
    datefmt='%d.%m.%y %H:%M:%S',
    encoding='utf-8',
)


class PasswordCheck(StatesGroup):
    password = State()


@dp.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    check_user = users.find_one({'user_id': user_id})
    if check_user is not None:
        await message.answer(INITIAL_TEXT)
    else:
        await message.answer('Введите пароль')
        await state.set_state(PasswordCheck.password)


@dp.message(PasswordCheck.password)
async def check_password(message: Message, state: FSMContext):
    if message.text == PASSWORD:
        await message.answer(INITIAL_TEXT)
        await state.clear()
    else:
        await message.answer('Пароль неверный, повторите попытку')
        return


async def main():
    scheduler = AsyncIOScheduler()
    # scheduler.add_job(
    #     send_remainder,
    #     'cron',
    #     day_of_week='mon, fri',
    #     hour=9,
    #     minute=0,
    #     timezone=constants.TIME_ZONE
    # )
    scheduler.add_job(
        send_quiz_button_in_chat,
        'cron',
        month='1,4,7,10',
        day=5,
        hour=2,
        minute=23,
        timezone=const.TIME_ZONE
    )
    scheduler.add_job(
        send_quiz_button,
        'cron',
        month='3,6,9,12',
        day=29,
        hour=10,
        minute=0,
        timezone=const.TIME_ZONE
    )
    # scheduler.add_job(
    #     send_tu_material,
    #     'cron',
    #     hour=10,
    #     minute=0,
    #     timezone=const.TIME_ZONE
    # )
    scheduler.start()
    # dp.include_router(service.router)
    # dp.include_router(registration.router)
    dp.include_router(admin_registration.router)
    # dp.include_router(plan.router)
    dp.include_router(quiz.router)
    # dp.include_router(import_questions.router)
    # dp.include_router(reports.router)
    # dp.include_router(key_rules.router)
    # dp.include_router(attentions.router)
    # dp.include_router(statistic.router)
    # dp.include_router(examen.router)
    dp.include_router(pb.router)
    # dp.include_router(videos.router)
    # dp.include_router(terms.router)  # всегда должен быть последним
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        filename='logs_bot.log',
        level=logging.INFO,
        filemode='a',
        format='%(asctime)s - %(message)s',
        datefmt='%d.%m.%y %H:%M:%S',
        encoding='utf-8',
    )
    asyncio.run(main())
