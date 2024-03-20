from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.utils import calc_date


def quiz_menu(test_type) -> InlineKeyboardMarkup:
    year, _, quarter = calc_date()
    kb = InlineKeyboardBuilder()
    kb.button(text='Нет', callback_data='exit')
    kb.button(text='Да', callback_data=(f'quiz_{year}_{quarter}_{test_type}'))
    kb.adjust(2)
    return kb.as_markup()


def themes_menu(themes) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Все вопросы!!!', callback_data=f'special__all')
    for theme in themes:
        kb.button(text=f'{theme["name"]}', callback_data=f'special__{theme["code"]}')
    kb.button(text='< Отмена >', callback_data='exit')
    kb.adjust(1)
    return kb.as_markup()
