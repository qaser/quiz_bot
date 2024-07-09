from aiogram_dialog.widgets.kbd import Button, Column, ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const, Format

from . import selected

SCROLLING_HEIGHT = 6


def category_buttons():
    return Column(
        Button(
            Const('📚 Выбрать тему'),
            'choose_theme',
            on_click=selected.on_chosen_themes
        ),
        Button(
            Const('🎲 Случайная статья'),
            'random',
            on_click=selected.on_random_article,
        ),
        Button(
            Const('🆕 Добавить новую статью'),
            'new_article',
            on_click=selected.on_new_article,
        )
    )


def paginated_themes(on_click):
    return ScrollingGroup(
        Select(
            Format('{item[0]}'),
            id='s_themes',
            item_id_getter=lambda x: x[1],
            items='themes',
            on_click=on_click,
        ),
        id='themes_pager',
        width=1,
        height=SCROLLING_HEIGHT,
        hide_pager=True,
        hide_on_single_page=True,
    )


def paginated_articles(on_click):
    return ScrollingGroup(
        Select(
            Format('{item[0]}'),
            id='s_articles',
            item_id_getter=lambda x: x[1],
            items='articles',
            on_click=on_click,
        ),
        id='articles_pager',
        width=1,
        height=SCROLLING_HEIGHT,
        hide_pager=True,
        hide_on_single_page=True,
    )
