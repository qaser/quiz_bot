import asyncio
import logging

from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
# from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config.bot_config import dp, bot
from handlers import start, service, terms, quiz
from utils.constants import HELP_TEXT, TIME_ZONE

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
    # scheduler = AsyncIOScheduler()
    # scheduler.add_job(
    #     send_quiz_button_in_chat,
    #     'cron',
    #     month='1,4,7,10',
    #     day=12,
    #     hour=8,
    #     minute=0,
    #     timezone=TIME_ZONE
    # )
    # scheduler.add_job(
    #     send_quiz_button_in_chat,
    #     'cron',
    #     month='3,6,9,12',
    #     day=29,
    #     hour=8,
    #     minute=0,
    #     timezone=TIME_ZONE
    # )
    # scheduler.add_job(
    #     send_tu_material,
    #     'cron',
    #     hour=8,
    #     minute=0,
    #     timezone=TIME_ZONE
    # )
    # scheduler.start()
    dp.include_routers(
        service.router,
        start.router,
        terms.router,
        quiz.router,
        terms.dialog,
        quiz.dialog,
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
