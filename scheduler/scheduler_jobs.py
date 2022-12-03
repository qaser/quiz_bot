from apscheduler.schedulers.asyncio import AsyncIOScheduler

import utils.constants as const
from scheduler.scheduler_func import add_questions_in_plan, send_quiz_button


scheduler = AsyncIOScheduler()


'''
рассылка будет первого числа нового квартала
по истечению 4 дней, если тест не пройден, будет напоминание, что приём завершается через 1 день
'''

def scheduler_jobs():
    scheduler.add_job(
        add_questions_in_plan,
        'cron',
        month='1,4,7,10',
        day=1,
        hour=7,
        minute=0,
        timezone=const.TIME_ZONE
    )
    scheduler.add_job(
        send_quiz_button,
        'cron',
        month='1,4,7,10',
        day=1,
        hour=10,
        minute=0,
        timezone=const.TIME_ZONE
    )
    scheduler.add_job(
        send_quiz_button,
        'cron',
        hour=12,
        minute=24,
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
