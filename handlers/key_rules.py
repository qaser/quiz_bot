from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.media_group import MediaGroupBuilder

from config.bot_config import bot
from config.mongo_config import key_rules


router = Router()

@router.message(Command('key_rules'))
async def send_key_rules(message: Message):
    photo_ids = [file_id.get('photo_id') for file_id in list(key_rules.find({}))]
    group_count = 0
    album_builder = MediaGroupBuilder(caption='Ключевые правила безопасности')
    for photo_id in photo_ids:
        # media_group.append(InputMediaPhoto(photo_id))
        album_builder.add_photo(photo_id)
        group_count += 1
        if group_count >= 6:
            await bot.send_media_group(chat_id=message.chat.id, media=album_builder.build())
            group_count = 0
            album_builder = MediaGroupBuilder(caption='Ключевые правила безопасности')
    # if 0 < group_count < 10:
    #     await bot.send_media_group(chat_id=message.chat.id, media=album_builder.build())
    await message.delete()
