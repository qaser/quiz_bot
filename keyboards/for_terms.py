from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu(terms_list) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for theme in terms_list:
        theme_code = theme['_id']['theme_code']
        theme_name = theme['_id']['name']
        kb.button(text=theme_name, callback_data=f'theme_{theme_code}')
    kb.button(text='< Выход >', callback_data='exit')
    kb.adjust(1)
    return kb.as_markup()


def theme_menu(theme_list) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for term in theme_list:
        term_id = term['_id']
        kb.button(text=term['name'], callback_data=f'term_{term_id}')
        kb.adjust(1)
    kb.row(
        InlineKeyboardButton(text='< Выход >', callback_data='exit'),
        InlineKeyboardButton(text='<< Назад', callback_data='back_theme_id'),
    )
    return kb.as_markup()


def term_menu(term_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text='< Выход >', callback_data='exit'),
        InlineKeyboardButton(text='<< Назад', callback_data=f'back_term_{term_id}'),
    )
    return kb.as_markup()
