from aiogram_dialog.widgets.kbd import (Button, Column, CurrentPage, FirstPage,
                                        LastPage, Multiselect, NextPage,
                                        NumberedPager, PrevPage, Row,
                                        ScrollingGroup, Select, StubScroll,
                                        SwitchTo)
from aiogram_dialog.widgets.text import Const, Format

from config.mongo_config import results, users

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
        # Button(
        #     Const('📝 Добавить новую статью'),
        #     'new_article',
        #     on_click=selected.on_new_article,
        #     when=is_admin
        # )
    )


def paginated_themes(id_pager):
    return ScrollingGroup(
        Select(
            Format('{item[0]}'),
            id='s_themes',
            item_id_getter=lambda x: x[1],
            items='themes',
        ),
        id=id_pager,
        width=1,
        height=SCROLLING_HEIGHT,
        hide_pager=True,
        hide_on_single_page=True,
    )
