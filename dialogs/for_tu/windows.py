from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import (Back, Button, Cancel, CurrentPage,
                                        Group, NextPage, PrevPage, Row, Select)
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
QUIZ_REPORT_LEGEND = ('<i>Синим кругом 🔵 отмечен Ваш ответ, правильный ответ '
                      '<u>подчеркнут</u></i>')


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


def quiz_window():
    return Window(
        Const('Темы, использованные для составления теста:'),
        Format('<b>{name_themes}</b>'),
        Format('\nВсего вопросов: <b>{quiz_len}</b>'),
        Button(
            Const('🚀 Начать тест'),
            id='quiz_start',
            on_click=selected.on_quiz_step
        ),
        state=Tu.quiz,
        getter=getters.get_quiz_params,
    )


def quiz_step_window():
    return Window(
        Format('<u>Вопрос {count} из {len}</u>'),
        Format('<b>Источник:</b> "{doc}"\n', when='doc_allows'),
        Format('<b>{text}</b>'),
        Const(
            '<i>(может быть несколько вариантов ответа)</i>',
            when='multiple'
        ),
        Format('\n{answers}'),
        keyboards.options_buttons(),
        Button(
            Const('Отправить ➜'),
            id='send_answer',
            on_click=selected.on_quiz_step,
        ),
        state=Tu.quiz_step,
        getter=getters.get_quiz_step,
    )


def quiz_result_window():
    return Window(
        Const('<u>Результат теста:</u>\n'),
        Format('Правильных ответов: {score} из {count}'),
        Format('Ваша оценка за тест: {grade} из 10-ти баллов\n'),
        Format(
            text=('❗ Наибольшее количество ошибок ({errors_num}) '
                  'Вы совершили на вопросах по теме "{theme_name}"\n'),
            when='with_errors'
        ),
        keyboards.result_buttons(),
        Cancel(Const('🔚 Выход'), on_click=on_click),
        state=Tu.quiz_result,
        getter=getters.get_quiz_result,
    )


def quiz_reports_window():
    return Window(
        Format('Вы прошли тестирования <b>{q}</b> кв. <b>{y}</b> года'),
        Const('Теперь Вы можете посмотреть результаты\n'),
        Format(
            ('<b>Входной тест</b> был пройден {input_date} '
             'c результатом {input_grade} из 10 баллов.\n'
             'Правильных ответов было {input_ans} из {input_quiz}\n'),
            when='input_access'
        ),
        Format(
            ('<b>Выходной тест</b> был пройден {output_date} '
             'c результатом {output_grade} из 10 баллов.\n'
             'Правильных ответов было {output_ans} из {output_quiz}'),
            when='output_access'
        ),
        Button(
            Const('➡️ Входной тест'),
            id='input_result',
            on_click=selected.on_chosen_quiz_report,
            when='input_access'
        ),
        Button(
            Const('➡️ Выходной тест'),
            id='output_result',
            on_click=selected.on_chosen_quiz_report,
            when='output_access'
        ),
        Back(Const(texts.BACK_BUTTON)),
        state=Tu.quiz_reports,
        getter=getters.get_quiz_reports,
    )


def quiz_chosen_report_window():
    return Window(
        Format('<u>Вопрос №{num}</u>'),
        Format('<b>{q_text}\n</b>'),
        Format('{ans_text}'),
        Const(QUIZ_REPORT_LEGEND),
        Group(
            Select(
                Format('{item[2]} {item[0]} '),
                id='report_select_question',
                item_id_getter=lambda i: f'{i[0]}_{i[1]}',
                items='options',
                on_click=selected.on_chosen_quiz_report
            ),
            id='report',
            width=5,
        ),
        Back(Const(texts.BACK_BUTTON)),
        state=Tu.quiz_chosen_report,
        getter=getters.get_chosen_quiz_report,
    )
