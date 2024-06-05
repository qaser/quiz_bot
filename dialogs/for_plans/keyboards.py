import datetime as dt

from aiogram_dialog.widgets.kbd import (
    ScrollingGroup, Column, Button, Select, Row, Multiselect
)
from aiogram_dialog.widgets.text import Format, Const

from . import selected
from config.mongo_config import plans

SCROLLING_HEIGHT = 6


def category_buttons():
    return Column(
        Button(
            Const('🧠 Составить тестовое задание'),
            'new_plan',
            on_click=selected.on_choose_category
        ),
        Button(
            Const('🔎 Обзор плана ТУ'),
            'show_plan',
            on_click=selected.on_choose_category,
        ),
        Button(
            Const('💾 Экспорт тестовых вопросов'),
            'export_test',
            on_click=selected.on_choose_category,
        ),
        Button(
            Const('📊 Экспорт результатов тестирования'),
            'export_test',
            on_click=selected.on_choose_category,
        ),
        Button(
            Const('📝 Планирование рассылки статей'),
            'sub_plan',
            on_click=selected.on_choose_category,
        ),
    )


def years_buttons():
    now_year = dt.datetime.now().year
    btns = [
        Button(
            Const(year),
            id=year,
            on_click=selected.on_year
        )
        for year in [str(now_year), str(now_year + 1)]
    ]
    return Row(*btns)


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
            max_selected=10
        ),
        id=id_pager,
        width=1,
        height=SCROLLING_HEIGHT,
        hide_pager=True,
        hide_on_single_page=True,
    )
