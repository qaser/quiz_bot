from aiogram import Dispatcher, types
from aiogram.types import InputMediaPhoto

from config.bot_config import bot
from config.mongo_config import key_rules


async def send_key_rules(message: types.Message):
    photo_ids = [file_id.get('photo_id') for file_id in list(key_rules.find({}))]
    media_group = []
    for photo_id in photo_ids:
        media_group.append(InputMediaPhoto(photo_id))
        if len(media_group) >= 6:
            await bot.send_media_group(chat_id=message.chat.id, media=media_group)
            media_group = []
    if 0 < len(media_group) < 6:
        await bot.send_media_group(chat_id=message.chat.id, media=media_group)
    await message.delete()


def register_handlers_key_rules(dp: Dispatcher):
    dp.register_message_handler(send_key_rules, commands='key_rules')
