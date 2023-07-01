from apscheduler.schedulers.asyncio import AsyncIOScheduler

import utils.constants as const
from scheduler.scheduler_func import send_quiz_button, send_tu_material, add_questions_in_plan

scheduler = AsyncIOScheduler()


def scheduler_jobs():
    scheduler.add_job(
        add_questions_in_plan,
        'cron',
        month='1,4,7,10',
        day=1,
        hour=11,
        minute=25,
        timezone=const.TIME_ZONE
    )
    scheduler.add_job(
        send_quiz_button,
        'cron',
        month='1,4,7,10',
        day=3,
        hour=10,
        minute=0,
        timezone=const.TIME_ZONE
    )
    scheduler.add_job(
        send_quiz_button,
        'cron',
        month='3,6,9,12',
        day=26,
        hour=10,
        minute=0,
        timezone=const.TIME_ZONE
    )
    scheduler.add_job(
        send_tu_material,
        'cron',
        hour=10,
        minute=0,
        timezone=const.TIME_ZONE
    )
    # scheduler.add_job(
    #     add_questions_in_plan,
    #     'cron',
    #     day=23,
    #     hour=23,
    #     minute=55,
    #     timezone=const.TIME_ZONE
    # )
