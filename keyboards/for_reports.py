from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def years_menu(years, user_id, mark) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for year in years:
        kb.button(
            text=str(year),
            callback_data=f'{mark}_y_{year}_{user_id}'
        )
    kb.adjust(3)
    return kb.as_markup()


def quarters_menu(year, user_id, mark) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for q in range(1, 5):
        kb.button(
            text=str(q),
            callback_data=f'{mark}_q_{q}_{year}_{user_id}'
        )
    kb.adjust(4)
    return kb.as_markup()


def type_test_menu(year, user_id, q) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for t_type in ['входной', 'выходной']:
        kb.button(
            text=str(t_type),
            callback_data=f'results_t_{t_type}_{q}_{year}_{user_id}'
        )
    kb.adjust(2)
    return kb.as_markup()
