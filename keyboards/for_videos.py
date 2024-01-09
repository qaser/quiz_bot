from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu(theme_list) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for theme in theme_list:
        theme_code = theme['_id']['theme_code']
        theme_name = theme['_id']['theme']
        kb.button(text=theme_name, callback_data=f'vid-theme_{theme_code}')
    kb.button(text='< Выход >', callback_data='vid-exit')
    kb.adjust(1)
    return kb.as_markup()


def subtheme_menu(subtheme_list) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for subtheme in subtheme_list:
        subtheme_code = subtheme['_id']['subtheme_code']
        subtheme_name = subtheme['_id']['subtheme']
        kb.button(text=subtheme_name, callback_data=f'vid-subtheme_{subtheme_code}')
        kb.adjust(1)
    kb.row(
        InlineKeyboardButton(text='< Выход >', callback_data='vid-exit'),
        InlineKeyboardButton(text='<< К разделам', callback_data='vid-back_subtheme_id'),
    )
    return kb.as_markup()


def videos_menu(video_list, subtheme_code) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for video in video_list:
        vid_id = video['_id']
        kb.button(text=video['title'], callback_data=f'vid-video_{vid_id}')
        kb.adjust(1)
    kb.row(
        InlineKeyboardButton(text='< Выход >', callback_data='vid-exit'),
        InlineKeyboardButton(
            text='<< К подразделам',
            callback_data=f'vid-back_videos_{subtheme_code}'
        )
    )
    return kb.as_markup()


def final_menu(video_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text='< Выход >', callback_data='vid-exit'),
        InlineKeyboardButton(
            text='<< Назад',
            callback_data=f'vid-back_show_{video_id}'
        )
    )
