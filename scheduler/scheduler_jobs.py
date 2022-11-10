from apscheduler.schedulers.asyncio import AsyncIOScheduler

import utils.constants as const
from handlers.quiz import send_quiz_shedule

scheduler = AsyncIOScheduler()


def scheduler_jobs():
    pass
    # по будням в 15:00 отправляет заметку о сегодняшнем дне
    # scheduler.add_job(
    #     send_history_day,
    #     'cron',
    #     day_of_week='mon-sun',
    #     hour=15,
    #     minute=0,
    #     timezone=const.TIME_ZONE
    # )
