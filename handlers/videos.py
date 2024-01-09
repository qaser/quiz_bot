from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, FSInputFile
from bson.objectid import ObjectId

from config.bot_config import bot
from config.mongo_config import videos
import keyboards.for_videos as kb


router = Router()

''' структура БД 'videos':
        _id: уникальный id
        theme: наименование раздела (например ОТ, ПБ, Оборудование и т.д.)
        theme_code: латинсое наименованое раздела (например ot)
        subtheme: подраздел в выбранной тематике (например СИЗ, СКЗ, ГПА и т.д.)
        subtheme_code: код на латинском
        title: название видео на кириллице
        link: уникальный номер ссылки на файл
'''


@router.message(Command('videos'))
async def videos_request(message: Message):
    pipeline = [
        {'$group': {'_id': {'theme_code': '$theme_code', 'theme': '$theme'}}}
    ]
    queryset = list(videos.aggregate(pipeline=pipeline))
    await message.delete()
    await message.answer(
        text=('Короткие обучающие видеоролики.\n'
              'Выберите раздел:'),
        reply_markup=kb.main_menu(queryset),
    )


@router.callback_query(F.data.startswith('vid-theme_'))
async def get_subtheme(call: CallbackQuery):
    _, theme_code = call.data.split('_')
    pipeline = [
        {'$match': {'theme_code': theme_code}},
        {'$group': {'_id': {'subtheme_code': '$subtheme_code', 'subtheme': '$subtheme'}}}
    ]
    queryset = list(videos.aggregate(pipeline=pipeline))
    await call.message.edit_text(
        'Выберите подраздел:',
        reply_markup=kb.subtheme_menu(queryset)
    )


@router.callback_query(F.data.startswith('vid-subtheme_'))
async def get_videos(call: CallbackQuery):
    _, subtheme_code = call.data.split('_')
    queryset = list(videos.find({'subtheme_code': subtheme_code}))
    await call.message.edit_text(
        'Выберите видео по названию:',
        reply_markup=kb.videos_menu(queryset, subtheme_code),
    )


@router.callback_query(F.data.startswith('vid-video_'))
async def send_video(call: CallbackQuery):
    _, vid_id = call.data.split('_')
    vid = videos.find_one({'_id': ObjectId(vid_id)})
    link = vid.get('link')
    title = vid.get('title')
    await call.message.delete()
    await call.message.answer_video(
        video=link,
        caption=title,
        reply_markup=kb.final_menu(vid_id)
    )


@router.callback_query(F.data.startswith('vid-back_'))
async def videos_menu_back(call: CallbackQuery):
    _, level, value = call.data.split('_')
    if level == 'subtheme':
        await videos_request(call.message)
    elif level == 'videos':
        # здесь value == subtheme_code
        theme_code = videos.find_one({'subtheme_code': value}).get('theme_code')
        pipeline = [
            {'$match': {'theme_code': theme_code}},
            {'$group': {'_id': {'subtheme_code': '$subtheme_code', 'subtheme': '$subtheme'}}}
        ]
        queryset = list(videos.aggregate(pipeline=pipeline))
        await call.message.edit_text(
            text='Выберите подраздел:',
            reply_markup=kb.subtheme_menu(queryset),
        )
    elif level == 'show':
        # здесь value == vid_id
        subtheme_code = videos.find_one({'_id': ObjectId(value)}).get('subtheme_code')
        queryset = list(videos.find({'subtheme_code': subtheme_code}))
        await call.message.delete()
        await call.message.answer(
            text='Выберите видео по названию:',
            reply_markup=kb.videos_menu(queryset, value),
        )


@router.callback_query(F.data.startswith('vid-exit'))
async def videos_exit(call: CallbackQuery):
    await call.message.delete()


@router.message(Command('vid'))
async def uploadVideoFiles(message: Message):
    path = f'static/videos/kontrol_vrz.mp4'
    video = FSInputFile(path=path)
    msg = await bot.send_video(message.chat.id, video)
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
