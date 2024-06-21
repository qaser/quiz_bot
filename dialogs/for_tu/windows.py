from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import (Back, Button, Cancel, CurrentPage,
                                        NextPage, PrevPage, Row)
from aiogram_dialog.widgets.text import Const, Format

import utils.constants as texts
from dialogs.custom_widgets.custom_calendar import CustomCalendar
from dialogs.for_tu.states import Tu

from . import getters, keyboards, selected

ID_SCROLL_PAGER = 'themes_pager'
PLANS_THEMES_TEXT = ('Выберите темы для составления квартального теста знаний '
                     'персонала.\nВы можете выбрать от одной до пятнадцати тем\n')
PLANS_THEME_WARNING = ('❗ <b>Вы выбрали 15 тем, выбор новых тем ограничен.\n'
                     'Чтобы изменить выбор просто нажмите на уже '
                     'выбранную тему, а затем выберите другую</b>\n')
PLAN_ALREADY_HAVE = ('❗ <b>План тестирования в эти год и квартал был создан ранее\n'
                     'Если Вы продолжите, то старые данные будут удалены\n')


async def on_click(callback, button, dialog_manager):
    try:
        await dialog_manager.done()
        await callback.message.delete()
    except:
        pass


def main_menu_window():
    return Window(
        Const('Модуль планирования технической учёбы'),
        keyboards.category_buttons(),
        Cancel(Const('🔚 Выход'), on_click=on_click),
        state=Tu.select_category,
    )


def select_year_window():
    return Window(
        Const('Выберите год планирования ТУ'),
        keyboards.years_buttons(),
        Back(Const(texts.BACK_BUTTON)),
        state=Tu.select_year,
    )


def select_quarter_window():
    return Window(
        Const('Выберите квартал планирования ТУ'),
        keyboards.quarters_buttons(),
        Back(Const(texts.BACK_BUTTON)),
        state=Tu.select_quarter,
    )


def select_themes_window():
    return Window(
        Const(PLANS_THEMES_TEXT),
        Const(PLANS_THEME_WARNING, when='warning'),
        Const(PLAN_ALREADY_HAVE, when='plan_it'),
        Format('🔷 <u>Выбрано тем: {themes_count}</u>'),
        keyboards.paginated_themes(ID_SCROLL_PAGER),
        Row(
            PrevPage(scroll=ID_SCROLL_PAGER, text=Format('<')),
            CurrentPage(scroll=ID_SCROLL_PAGER, text=Format('{current_page1} / {pages}')),
            NextPage(scroll=ID_SCROLL_PAGER, text=Format('>'))
        ),
        Button(
            Const(texts.NEXT_BUTTON),
            id='select_date',
            on_click=selected.on_themes_done,
            when='chosen_one'
        ),
        Back(Const(texts.BACK_BUTTON)),
        state=Tu.select_themes,
        getter=getters.get_themes
    )


def select_date_window():
    return Window(
        Format(
            ('Выберите дату рассылки тестового задания в '
             '<u>{period}</u> {q} кв. {y}г.\n'
             '<b>Подсказка:</b> найдите в календаре <u>{y}</u> год, '
             'затем <u>{m}</u> и выберите дату')
        ),
        CustomCalendar(
            id='calendar',
            on_click=selected.on_select_date,
        ),
        Back(Const(texts.BACK_BUTTON)),
        getter=getters.get_plan_params,
        state=Tu.select_date
    )


def save_plan_window():
    return Window(
        Format('Данные сохранены'),
        Cancel(Const('🔚 Выход'), on_click=on_click),
        state=Tu.save_plan
    )
