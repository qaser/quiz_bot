import asyncio
import os

import pymongo
from aiogram import Bot
from aiogram.contrib.fsm_storage.mongo import MongoStorage
from dotenv import load_dotenv

load_dotenv()

# Create the client
client = pymongo.MongoClient('localhost', 27017)
storage = MongoStorage(host='localhost', port=27017, db_name='aiogram_fsm')
db = client['quiz_db']
videos = db['videos']
# terms = db['terms']
# key_rules = db['key_rules']

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
ADMIN_TELEGRAM_ID = os.getenv('ADMIN_TELEGRAM_ID')



bot = Bot(token=TELEGRAM_TOKEN)


BASE_MEDIA_PATH = './static'


async def uploadVideoFiles(folder, method, file_attr):
    folder_path = os.path.join(BASE_MEDIA_PATH, folder)
    for filename in os.listdir(folder_path):
        if filename.startswith('.'):
            continue
        with open(os.path.join(folder_path, filename), 'rb') as file:
            msg = await method(ADMIN_TELEGRAM_ID, file, disable_notification=True)
            if file_attr == 'video':
                file_id = msg.video[-1].file_id
            else:
                file_id = getattr(msg, file_attr).file_id
            videos.insert_one(
                {
                    'theme': 'Охрана труда',
                    'theme_code': 'ot',
                    'subtheme': 'СИЗ',
                    'subtheme_code': 'siz',
                    'title': 'ПШ-1',
                    'link': file_id,
                }
            )


loop = asyncio.get_event_loop()

tasks = [
    loop.create_task(uploadVideoFiles('videos', bot.send_video, 'video')),
]

wait_tasks = asyncio.wait(tasks)

loop.run_until_complete(wait_tasks)
loop.close()
