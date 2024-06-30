import datetime as dt

from aiogram_dialog.widgets.kbd import (Button, Column, Group, Multiselect,
                                        Radio, Row, ScrollingGroup, Select)
from aiogram_dialog.widgets.text import Const, Format

from config.mongo_config import plans

from . import selected

SCROLLING_HEIGHT = 6


def category_buttons():
    return Column(
        Button(
            Const('✍️ Составить тестовое задание'),
            'new_plan',
            on_click=selected.on_choose_category
        ),
        # Button(
        #     Const('🔎 Обзор тестовых заданий ТУ'),
        #     'plan_review',
        #     on_click=selected.on_choose_category,
        # ),
        Button(
            Const('👷🏻‍♂️ Просмотр результатов тестирования'),
            'results_review',
            on_click=selected.on_choose_category,
        ),
        # Button(
        #     Const('📈 Посмотреть статистику персонала'),
        #     'stats',
        #     on_click=selected.on_choose_category,
        # ),
        Button(
            Const('💾 Экспорт тестовых вопросов (.docx)'),
            'test_export',
            on_click=selected.on_choose_category,
        ),
        Button(
            Const('📥 Экспорт результатов тестирования (.docx)'),
            'results_export',
            on_click=selected.on_choose_category,
        ),
        # Button(
        #     Const('📝 Планирование рассылки статей'),
        #     'sub_plan',
        #     on_click=selected.on_choose_category,
        # ),
    )


def years_buttons():
    return Group(
        Select(
            Format('{item}'),
            id='select_years',
            item_id_getter=lambda x: x,
            items='years',
            on_click=selected.on_year,
        ),
        id='years',
        width=2,
    )


def quarters_buttons():
    btns = [
        Button(
            Const(str(q)),
            id=str(q),
            on_click=selected.on_quarter
        )
        for q in range(1, 5)
    ]
    return Row(*btns)


def paginated_themes(id_pager):
    return ScrollingGroup(
        Multiselect(
            Format('🟢 {item[name]}'),
            Format('⚪ {item[name]}'),
            id='s_themes',
            item_id_getter=lambda x: x['code'],
            items='themes',
            min_selected=1,
            max_selected=15
        ),
        id=id_pager,
        width=1,
        height=SCROLLING_HEIGHT,
        hide_pager=True,
        hide_on_single_page=True,
    )


def paginated_users(id_pager):
    return ScrollingGroup(
        Select(
            Format('{item[username]}'),
            id='s_users',
            item_id_getter=lambda x: x['user_id'],
            items='users',
            on_click=selected.on_user_results
        ),
        id=id_pager,
        width=2,
        height=SCROLLING_HEIGHT,
        hide_pager=True,
        hide_on_single_page=True,
    )


def options_buttons():
    return Row(
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
            on_click=selected.on_quiz_reports,
            when='report_access'
        ),
        id='result_btns'
    )


def is_no_multiple(data, widget, manager):
    ctx = manager.current_context()
    is_multiple = ctx.dialog_data['quiz_step']['multiple']
    return not is_multiple
