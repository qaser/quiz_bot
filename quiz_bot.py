import asyncio
import logging

from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config.bot_config import dp, bot
from handlers import (
    start, service, terms, quiz, options, articles, admin, blpu, plans
)
from scheduler.scheduler_func import check_tu_events
from utils.constants import HELP_TEXT, TIME_ZONE
from middlewares.check_user import CheckUserMiddleware

from aiogram_dialog import setup_dialogs


@dp.message(Command('reset'))
async def reset_handler(message: Message, state: FSMContext):
    await message.delete()
    await state.clear()
    await message.answer(
        'Текущее состояние бота сброшено',
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message(Command('help'))
async def help_handler(message: Message):
    await message.answer(HELP_TEXT)


async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        check_tu_events,
        'cron',
        hour=10,
        minute=0,
        timezone=TIME_ZONE
    )
    scheduler.start()
    dp.update.outer_middleware(CheckUserMiddleware())
    dp.include_routers(
        service.router,
        start.router,
        admin.router,
        terms.router,
        quiz.router,
        options.router,
        articles.router,
        blpu.router,
        plans.router,
        terms.dialog,
        quiz.dialog,
        options.dialog,
        articles.dialog,
        blpu.dialog,
        plans.dialog,
    )
    setup_dialogs(dp)
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
