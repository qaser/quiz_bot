from aiogram import F, Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command

from config.bot_config import bot
from config.mongo_config import users
from config.telegram_config import ADMIN_TELEGRAM_ID
from utils.constants import HELP_TEXT
from utils.decorators import superuser_check


router = Router()

@superuser_check
@router.message(Command('users'))
async def count_users(message: Message):
    queryset = users.distinct('full_name')
    users_count = len(queryset)
    final_text = '\n'.join(queryset)
    await message.answer(
        text=f'Количество пользователей в БД: {users_count}\n{final_text}'
    )


@superuser_check
@router.message(Command('log'))
async def send_logs(message: Message):
    document = FSInputFile(path=r'logs_bot.log')
    await message.answer_document(document=document)
    await message.delete()


@router.message(Command('help'))
async def help_handler(message: Message):
    await message.answer(HELP_TEXT)
