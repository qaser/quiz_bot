from aiogram import Router
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message

from config.mongo_config import users
from config.telegram_config import ADMIN_TELEGRAM_ID

router = Router()


@router.message(Command('users'))
async def count_users(message: Message):
    user_id = message.from_user.id
    if user_id == int(ADMIN_TELEGRAM_ID):
        users_count = users.count_documents({})
        await message.answer(
            text=f'Количество пользователей в БД: {users_count}'
        )
    await message.delete()


@router.message(Command('log'))
async def send_logs(message: Message):
    user_id = message.from_user.id
    if user_id == int(ADMIN_TELEGRAM_ID):
        document = FSInputFile(path=r'logs_bot.log')
        await message.answer_document(document=document)
    await message.delete()
