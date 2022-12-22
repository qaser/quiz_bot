import os

from aiogram import Dispatcher, types
from aiogram.types import InputMediaPhoto
from aiogram.dispatcher.filters import Text

from config.bot_config import bot, dp
from config.mongo_config import attentions


async def choose_year_attentions(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    years = attentions.distinct('year')
    for year in years:
        keyboard.add(types.InlineKeyboardButton(text=f'{year}', callback_data=f'attention_{year}'))
    await message.delete()
    await message.answer('Выберите год', reply_markup=keyboard)


@dp.callback_query_handler(Text(startswith='attention_'))
async def sent_attentions(call: types.CallbackQuery):
    _, year = call.data.split('_')
    photo_ids = [file_id.get('_id') for file_id in list(attentions.find({'year': int(year)}))]
    media_group = []
    for photo_id in photo_ids:
        media_group.append(InputMediaPhoto(photo_id))
        if len(media_group) >= 6:
            await bot.send_media_group(chat_id=call.message.chat.id, media=media_group)
            media_group = []
    if 0 < len(media_group) < 6:
        await bot.send_media_group(chat_id=call.message.chat.id, media=media_group)
    await call.message.delete()


def register_handlers_attentions(dp: Dispatcher):
    dp.register_message_handler(choose_year_attentions, commands='vnimanie')
