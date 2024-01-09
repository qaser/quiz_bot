import asyncio
import os

import pymongo
from aiogram import Bot
from dotenv import load_dotenv
from aiogram.types import Message, CallbackQuery, FSInputFile

load_dotenv()

# Create the client
client = pymongo.MongoClient('localhost', 27017)
db = client['quiz_db']
videos = db['videos']


TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
ADMIN_TELEGRAM_ID = os.getenv('ADMIN_TELEGRAM_ID')



bot = Bot(token=TELEGRAM_TOKEN)


BASE_MEDIA_PATH = './static'


async def uploadVideoFiles():
    path = f'static/videos/kontrol_vrz.mp4'
    video = FSInputFile(path=path)
    msg = await bot.send_video(ADMIN_TELEGRAM_ID, video, disable_notification=True)
    file_id = getattr(msg).file_id
    videos.insert_one(
        {
            'theme': 'Охрана труда',
            'theme_code': 'ot',
            'subtheme': 'Контроль ВРЗ',
            'subtheme_code': 'vrz',
            'title': 'Периодический контроль',
            'link': file_id,
        }
    )

loop = asyncio.get_event_loop()

tasks = [
    loop.create_task(uploadVideoFiles()),
]

wait_tasks = asyncio.wait(tasks)

loop.run_until_complete(wait_tasks)
loop.close()
