from apscheduler.schedulers.asyncio import AsyncIOScheduler

import utils.constants as const
from scheduler.scheduler_func import send_quiz_button, send_quiz_button_in_chat

scheduler = AsyncIOScheduler()


def scheduler_jobs():
    scheduler.add_job(
        send_quiz_button_in_chat,
        'cron',
        month='1,4,7,10',
        day=5,
        hour=13,
        minute=15,
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
