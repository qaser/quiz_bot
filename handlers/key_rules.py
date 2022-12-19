from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from config.bot_config import bot, dp
from config.mongo_config import terms, key_rules
from bson.objectid import ObjectId
import os
from aiogram.types import InputMediaPhoto


async def send_key_rules(message: types.Message):
    photo_ids = [file_id.get('photo_id') for file_id in list(key_rules.find({}))]
    count = 0
    media_group = []
    for photo_id in photo_ids:
        count += 1
        media_group.append(InputMediaPhoto(photo_id))
        if count >= 6:
            await bot.send_media_group(chat_id=message.chat.id, media=media_group)
            media_group = []
            count = 0





def register_handlers_key_rules(dp: Dispatcher):
    dp.register_message_handler(send_key_rules, commands='key_rules')
