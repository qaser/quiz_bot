from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def accept_or_deny(user_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Принять', callback_data=f'admin_{user_id}_accept')
    kb.button(text='Отклонить', callback_data=f'admin_{user_id}_deny')
    kb.adjust(1)
    return kb.as_markup()


def get_yes_no_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text='Нет')
    kb.button(text='Да')
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
