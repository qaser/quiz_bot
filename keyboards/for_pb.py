from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Поиск ответа по тексту вопроса', callback_data='rpo_none_search')
    kb.button(text='Обучение для рабочих', callback_data='rpo_isp_learn')
    kb.button(text='Самопроверка для рабочих', callback_data='rpo_isp_test')
    kb.button(text='Обучение для ИТР', callback_data='rpo_itr_learn')
    kb.button(text='Самопроверка для ИТР', callback_data='rpo_itr_test')
    kb.adjust(1)
    return kb.as_markup()


def learn_menu(employee, count) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(
            text='Завершить',
            callback_data=f'learning_finish_{employee}_{count}'
        ),
        InlineKeyboardButton(
            text='Следующий',
            callback_data=f'learning_next_{employee}_{count+1}'
        )
    )
    return kb.as_markup()


def learning_menu(employee) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Начать заново', callback_data=f'learn_{employee}_new')
    kb.button(text='Продолжить', callback_data=f'learn_{employee}_continue')
    kb.adjust(1)
    return kb.as_markup()


def question_result_menu(employee) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(
            text='Завершить',
            callback_data=f'testing_{employee}_exit'
        ),
        InlineKeyboardButton(
            text='Следующий',
            callback_data=f'testing_{employee}_next'
        )
    )
    return kb.as_markup()


def variants_btns(employee, answers_query, question_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for ans in answers_query:
        sort_num = ans.get('sort_number')
        kb.button(
            text=sort_num,
            callback_data=f'answer_{employee}_{ans.get("p_id")}_{question_id}'
        )
    kb.adjust(5)
    return kb.as_markup()


def test_menu(employee):
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text='Отмена', callback_data=f'test_{employee}_exit'),
        InlineKeyboardButton(text='Начать', callback_data=f'test_{employee}_start')
    )
    return kb.as_markup()


def search_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Найти ещё', callback_data='search_next')
    return kb.as_markup()
