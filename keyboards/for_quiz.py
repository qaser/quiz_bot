from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.utils import calc_date


def quiz_menu(test_type, user_id) -> InlineKeyboardMarkup:
    year, _, quarter = calc_date()
    kb = InlineKeyboardBuilder()
    kb.button(text='Нет', callback_data='exit')
    kb.button(text='Да', callback_data=(f'quiz_{year}_{quarter}_{test_type}_{user_id}'))
    kb.adjust(2)
    return kb.as_markup()
