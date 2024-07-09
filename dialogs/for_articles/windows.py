from aiogram_dialog import Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import (Back, Button, Cancel, CurrentPage,
                                        NextPage, PrevPage, Row, Url)
from aiogram_dialog.widgets.text import Const, Format

import utils.constants as texts
from dialogs.for_articles.states import Articles

from . import getters, keyboards, selected

ARTICLES_RULES = (
    '<b>Правила публикации статей и учебных материалов:</b>\n\n'
    '1. Статью необходимо размещать на сайте https://telegra.ph/;\n'
    '2. При выборе тематики статьи отдавайте предпочтение техническим темам, '
    'которые будут актуальны продолжительное время;\n'
    '3. При написании статьи запрещено использовать фотографии оборудования, '
    'рабочих мест, территории предприятий и т.п., по которым можно однозначно '
    'определить их местонахождение и принадлежность;\n'
    '4. В начале статьи необходимо указать источники информации. '
    'Например: СТО Газпром 2-3.5-454-2010 (ПЭМГ), название книги или журнала с указанием авторства;\n'
    '5. После размещения статьи на сайте необходимо скопировать ссылку на неё и '
    'внести при добавлении статьи в этом приложении;\n'
    '6. После того как новая статья будет внесена в базу данных приложения она '
    'проходит модерацию и потом будет доступна для чтения;\n'
    '7. Дополнительно про сайт Telegraph можете почитать здесь -> '
    'https://vc.ru/u/1849221-strategiya-razvitiya/690024-pishem-statyu-v-telegraph-kak-pravilno-oformit-i-opublikovat'
)
ARTICLE_SAVE = (
    'Ваша статья сохранена и отправлена на модерацию.\n'
    'Вам придет сообщение о результате проверки'
)


async def exit_menu(callback, button, dialog_manager):
    try:
        await dialog_manager.done()
        await callback.message.delete()
    except:
        pass


def category_window():
    return Window(
        Const('Статьи и обучающие материалы'),
        keyboards.category_buttons(),
        Cancel(Const('🔚 Выход'), on_click=exit_menu),
        state=Articles.select_category,
    )


def random_article_window():
    return Window(
        Format('Случайная статья на тему "{theme}"'),
        Url(Format('{title}'), Format('{link}')),
        Button(
            Const(texts.BACK_BUTTON),
            id='back_to_main_menu',
            on_click=selected.on_main_menu
        ),
        state=Articles.random_article,
        getter=getters.get_random_article,
    )


def select_themes_window():
    return Window(
        Const('Выберите тему:'),
        keyboards.paginated_themes(selected.on_theme_done),
        Row(
            PrevPage(scroll='themes_pager', text=Format('<')),
            CurrentPage(
                scroll='themes_pager',
                text=Format('{current_page1} / {pages}')
            ),
            NextPage(scroll='themes_pager', text=Format('>')),
            when='is_paginated'
        ),
        Back(Const(texts.BACK_BUTTON)),
        state=Articles.select_themes,
        getter=getters.get_themes,
    )


def select_articles_window():
    return Window(
        Const('Выберите статью по названию:'),
        keyboards.paginated_articles(selected.on_articles_name),
        Row(
            PrevPage(scroll='articles_pager', text=Format('<')),
            CurrentPage(
                scroll='articles_pager',
                text=Format('{current_page1} / {pages}')
            ),
            NextPage(scroll='articles_pager', text=Format('>')),
            when='is_paginated'
        ),
        Back(Const(texts.BACK_BUTTON)),
        state=Articles.select_articles,
        getter=getters.get_articles,
    )


def article_url_window():
    return Window(
        Format('Выбранная статья на тему "{theme}"'),
        Format('{title}'),
        Format('{link}'),
        Back(Const(texts.BACK_BUTTON)),
        state=Articles.article_url,
        getter=getters.get_article_url,
    )


def new_article_window():
    return Window(
        Const(ARTICLES_RULES),
        Button(
            Const('Принять и продолжить 🔜'),
            id='article_rules',
            on_click=selected.on_chosen_themes
        ),
        Button(
            Const(texts.BACK_BUTTON),
            id='back_to_main_menu',
            on_click=selected.on_main_menu
        ),
        state=Articles.article_rules,
        disable_web_page_preview=True
    )


def input_article_name_window():
    return Window(
        Const('Введите название статьи'),
        Back(Const(texts.BACK_BUTTON)),
        TextInput(
            id='article_name',
            on_success=selected.on_save_article_name,
        ),
        state=Articles.input_article_name
    )


def input_article_url_window():
    return Window(
        Const('Введите ссылку на статью'),
        Back(Const(texts.BACK_BUTTON)),
        TextInput(
            id='article_url',
            on_success=selected.on_save_article,
        ),
        state=Articles.input_article_url,
        disable_web_page_preview=True
    )


def save_article_window():
    return Window(
        Const(ARTICLE_SAVE),
        Cancel(Const('🔚 Выход'), on_click=exit_menu),
        state=Articles.article_save_done
    )
