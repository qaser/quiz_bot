from aiogram_dialog.widgets.kbd import (Radio, Column, Button,
                                        ScrollingGroup, Multiselect, Row)
from aiogram_dialog.widgets.text import Format, Const

from . import selected
from config.mongo_config import users, results

SCROLLING_HEIGHT = 6


def main_menu_buttons():
    return Column(
        Button(
            Const('🆕 Новое тестирование'),
            'new_test',
            on_click=selected.on_choose_themes
        ),
        Button(
            Const('📈 Моя статистика'),
            'my_stats',
            on_click=selected.on_stats,
            when=no_first_quiz
        ),
        # Button(
        #     Const('📝 Добавить вопросы в БД'),
        #     'add_questions',
        #     on_click=selected.on_adding_questions,
        #     when=is_admin
        # )
    )


def paginated_themes():
    return ScrollingGroup(
        Multiselect(
            Format('🟢 {item[name]}'),
            Format('⚪ {item[name]}'),
            id='s_themes',
            item_id_getter=lambda x: x['code'],
            items='themes',
            min_selected=0,
            max_selected=5
        ),
        id='themes_page',
        width=1,
        height=SCROLLING_HEIGHT
    )


def len_quiz_buttons():
    return Radio(
        Format('🟢 {item}'),
        Format('⚪ {item}'),
        id='quiz_len',
        item_id_getter=lambda x: x,
        items=['15', '20', '30'],
    )


def options_buttons():
    return Row(
        # Multiselect(
        #     Format('🟢 {item[0]}'),
        #     Format('⚪ {item[0]}'),
        #     id='user_answers',
        #     item_id_getter=lambda x: x[1],
        #     items='options',
        #     when='multiple',
        #     min_selected=0,
        #     max_selected=10,
        # ),
        Radio(
            Format('🟢 {item[0]}'),
            Format('⚪ {item[0]}'),
            id='user_answers',
            item_id_getter=lambda x: x[1],
            items='options',
            when=is_no_multiple
        ),
    )


def result_buttons():
    return Column(
        Button(
            Const('📝 Посмотреть подробный отчёт'),
            id='quiz_report',
            on_click=selected.on_quiz_report
        ),
        Button(
            Const('⚡ Посмотреть рекомендации'),
            id='guideline',
            on_click=selected.on_quiz_guideline,
            when='have_articles'
        ),
        Button(
            Const('🔚 Главное меню'),
            id='main_menu',
            on_click=selected.on_main_menu
        ),
        id='result_btns'
    )


def is_no_multiple(data, widget, manager):
    ctx = manager.current_context()
    is_multiple = ctx.dialog_data['quiz_step']['multiple']
    return not is_multiple


def is_admin(data, widget, manager):
    user_id = manager.event.from_user.id
    is_admin = users.find_one({'user_id': user_id}).get('is_admin', False)
    return is_admin


def no_first_quiz(data, widget, manager):
    user_id = manager.event.from_user.id
    res = results.count_documents({'user_id': user_id})
    return True if res > 0 else False