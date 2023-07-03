from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.types import InputMediaVideo
from bson.objectid import ObjectId

from config.bot_config import bot, dp
from config.mongo_config import videos


''' структура БД 'videos':
        _id: уникальный id
        theme: наименование раздела (например ОТ, ПБ, Оборудование и т.д.)
        theme_code: латинсое наименованое раздела (например ot)
        subtheme: подраздел в выбранной тематике (например СИЗ, СКЗ, ГПА и т.д.)
        subtheme_code: код на латинском
        title: название видео на кириллице
        link: уникальный номер ссылки на файл
'''


async def videos_request(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    pipeline = [
        {'$group': {'_id': {'theme_code': '$theme_code', 'theme': '$theme'}}}
    ]
    queryset = list(videos.aggregate(pipeline=pipeline))
    for theme in queryset:
        theme_code = theme['_id']['theme_code']
        theme_name = theme['_id']['theme']
        keyboard.add(
            types.InlineKeyboardButton(
                text=theme_name,
                callback_data=f'vid-theme_{theme_code}'
            )
        )
    keyboard.add(
        types.InlineKeyboardButton(text='< Выход >', callback_data='vid-exit'),
    )
    await message.delete()
    await message.answer(
        text=('Короткие обучающие видеоролики.\n'
              'Выберите раздел:'),
        reply_markup=keyboard,
    )


@dp.callback_query_handler(Text(startswith='vid-theme_'))
async def get_subtheme(call: types.CallbackQuery):
    _, theme_code = call.data.split('_')
    pipeline = [
        {
            '$match': {'theme_code': theme_code},
            '$group': {'_id': {'subtheme_code': '$subtheme_code', 'subtheme': '$subtheme'}}
        }
    ]
    keyboard = types.InlineKeyboardMarkup()
    queryset = list(videos.aggregate(pipeline=pipeline))
    for subtheme in queryset:
        subtheme_code = subtheme['_id']['subtheme_code']
        subtheme_name = subtheme['_id']['subtheme']
        keyboard.add(
            types.InlineKeyboardButton(
                text=subtheme_name,
                callback_data=f'vid-subtheme_{subtheme_code}'
            )
        )
    keyboard.row(
        types.InlineKeyboardButton(text='< Выход >', callback_data='exit'),
        types.InlineKeyboardButton(text='<< К разделам', callback_data='vid-back_subtheme_id'),
    )
    await call.message.edit_text(
        'Выберите подраздел:',
        reply_markup=keyboard,
    )


@dp.callback_query_handler(Text(startswith='vid-subtheme_'))
async def get_videos(call: types.CallbackQuery):
    _, subtheme_code = call.data.split('_')
    keyboard = types.InlineKeyboardMarkup()
    queryset = list(videos.find({'subtheme': subtheme_code}))
    for video in queryset:
        vid_id = video['_id']
        keyboard.add(
            types.InlineKeyboardButton(
                text=video['title'],
                callback_data=f'vid-video_{vid_id}'
            )
        )
    keyboard.row(
        types.InlineKeyboardButton(text='< Выход >', callback_data='vid-exit'),
        types.InlineKeyboardButton(text='<< К подразделам', callback_data=f'vid-back_videos_{subtheme_code}'),
    )
    await call.message.edit_text(
        'Выберите видео по названию:',
        reply_markup=keyboard,
    )


@dp.callback_query_handler(Text(startswith='vid-video_'))
async def send_video(call: types.CallbackQuery):
    _, vid_id = call.data.split('_')
    keyboard = types.InlineKeyboardMarkup()
    vid = videos.find_one({'_id': ObjectId(vid_id)})
    link = vid.get('link')
    title = vid.get('title')
    keyboard.row(
        # types.InlineKeyboardButton(text='< Выход >', callback_data='vid-exit'),
        types.InlineKeyboardButton(text='<< Назад', callback_data=f'vid-back_show_{vid_id}'),
    )
    await call.message.delete()
    await call.message.answer_video(
        video=link,
        caption=title,
        reply_markup=keyboard
    )


@dp.callback_query_handler(Text(startswith='vid-back_'))
async def videos_menu_back(call: types.CallbackQuery):
    _, level, value = call.data.split('_')
    if level == 'subtheme':
        await videos_request(call.message)
    elif level == 'videos':
        # здесь value == subtheme_code
        theme_code = videos.find_one({'subtheme_code': value}).get('theme_code')
        pipeline = [
            {
                '$match': {'theme_code': theme_code},
                '$group': {'_id': {'subtheme_code': '$subtheme_code', 'subtheme': '$subtheme'}}
            }
        ]
        keyboard = types.InlineKeyboardMarkup()
        queryset = list(videos.aggregate(pipeline=pipeline))
        for subtheme in queryset:
            subtheme_code = subtheme['_id']['subtheme_code']
            subtheme_name = subtheme['_id']['subtheme']
            keyboard.add(
                types.InlineKeyboardButton(
                    text=subtheme_name,
                    callback_data=f'vid-subtheme_{subtheme_code}'
                )
            )
        keyboard.row(
            types.InlineKeyboardButton(text='< Выход >', callback_data='exit'),
            types.InlineKeyboardButton(text='<< К разделам', callback_data='vid-back_theme_id'),
        )
        await call.message.edit_text(
            'Выберите подраздел:',
            reply_markup=keyboard,
        )
    elif level == 'show':
        # здесь value == vid_id
        subtheme_code = videos.find_one({'_id': ObjectId(value)}).get('subtheme_code')
        keyboard = types.InlineKeyboardMarkup()
        queryset = list(videos.find({'subtheme_code': subtheme_code}))
        for video in queryset:
            vid_id = video['_id']
            keyboard.add(
                types.InlineKeyboardButton(
                    text=video['title'],
                    callback_data=f'vid-video_{vid_id}'
                )
            )
        keyboard.row(
            types.InlineKeyboardButton(text='< Выход >', callback_data='vid-exit'),
            types.InlineKeyboardButton(text='<< К подразделам', callback_data=f'vid-back_videos_{subtheme_code}'),
        )
        await call.message.edit_text(
            'Выберите видео по названию:',
            reply_markup=keyboard,
        )


@dp.callback_query_handler(text='vid-exit')
async def videos_exit(call: types.CallbackQuery):
    await call.message.delete()


def register_handlers_videos(dp: Dispatcher):
    dp.register_message_handler(videos_request, commands='videos')
