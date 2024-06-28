import asyncio
import logging

from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram_dialog import setup_dialogs
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config.bot_config import bot, dp
from handlers import (admin, articles, blpu, options, quiz, service, start,
                      terms, tu)
from middlewares.check_user import CheckUserMiddleware
from scheduler.scheduler_func import check_tu_events, send_news
from utils.constants import HELP_TEXT, TIME_ZONE


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
        minute=15,
        timezone=TIME_ZONE
    )
    # scheduler.add_job(
    #     send_news,
    #     'cron',
    #     day_of_week='mon-sun',
    #     hour=10,
    #     minute=0,
    #     timezone=TIME_ZONE
    # )
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
        tu.router,
        terms.dialog,
        quiz.dialog,
        options.dialog,
        articles.dialog,
        blpu.dialog,
        tu.dialog,
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
