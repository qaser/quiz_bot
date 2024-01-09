from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def users_menu(user_id, buffer_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text='Отправить',
        callback_data=f'buffer_{user_id}_{buffer_id}'
    )
    kb.button(text='Отмена', callback_data=f'exit')
    kb.adjust(1)
    return kb.as_markup()
