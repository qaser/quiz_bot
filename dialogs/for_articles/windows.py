from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import (Back, Button, Cancel, CurrentPage,
                                        LastPage, NextPage, PrevPage, Row,
                                        Select, Url)
from aiogram_dialog.widgets.text import Const, Format

import utils.constants as texts
from dialogs.for_articles.states import Articles

from . import getters, keyboards, selected

ID_SCROLL_PAGER = 'themes_pager'
ARTICLES_THEME = 'Выберите тематику статей'


async def on_click(callback, button, dialog_manager):
    try:
        await dialog_manager.done()
        await callback.message.delete()
    except:
        pass


def category_window():
    return Window(
        Const('<b>Статьи и обучающие материалы</b>'),
        keyboards.category_buttons(),
        Cancel(Const('🔚 Выход'), on_click=on_click),
        state=Articles.select_category,
    )


def random_article_window():
    return Window(
        Const('<u>Случайная статья</u>'),
        Url(Format('{title}'), Format('{link}')),
        Back(Const(texts.BACK_BUTTON)),
        state=Articles.random_article,
        getter=getters.get_random_article,
    )


def select_themes_window():
    return Window(
        Const(ARTICLES_THEME),
        keyboards.paginated_themes(ID_SCROLL_PAGER),
        Row(
            PrevPage(scroll=ID_SCROLL_PAGER, text=Format('<')),
            CurrentPage(
                scroll=ID_SCROLL_PAGER,
                text=Format('{current_page1} / {pages}')
            ),
            NextPage(scroll=ID_SCROLL_PAGER, text=Format('>'))

        ),
        Button(
            Const(texts.NEXT_BUTTON),
            id='themes_done',
            on_click=selected.on_themes_done
        ),
        Back(Const(texts.BACK_BUTTON)),
        state=Articles.select_themes,
        getter=getters.get_themes,
    )
