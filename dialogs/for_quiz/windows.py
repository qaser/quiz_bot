from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Cancel, Back, Button, Group, Select
from aiogram_dialog.widgets.text import Format, Const

from . import keyboards, getters, selected, states
import utils.constants as texts


async def exit_click(callback, button, dialog_manager):
    try:
        await dialog_manager.done()
        await callback.message.delete()
    except:
        pass


def quiz_main_window():
    return Window(
        Const(texts.QUIZ_START_TEXT),
        keyboards.main_menu_buttons(),
        Cancel((Const(texts.EXIT_BUTTON)), on_click=exit_click),
        state=states.Quiz.select_category,
    )


def themes_window():
    return Window(
        Const(texts.QUIZ_THEMES_TEXT),
        Const(texts.QUIZ_THEME_WARNING, when='warning'),
        Format('🔷 <u>Выбрано тем: {themes_count}</u>'),
        keyboards.paginated_themes(),
        Button(
            Const(texts.NEXT_BUTTON),
            id='themes_done',
            on_click=selected.on_themes_done
        ),
        Back(Const(texts.BACK_BUTTON)),
        state=states.Quiz.select_themes,
        getter=getters.get_themes,
        parse_mode='HTML'
    )


def len_quiz_window():
    return Window(
        Const(texts.QUIZ_LEN_TEXT),
        keyboards.len_quiz_buttons(),
        Button(
            Const(texts.NEXT_BUTTON),
            id='quiz_params',
            on_click=selected.on_quiz_params
        ),
        Back(Const(texts.BACK_BUTTON)),
        state=states.Quiz.select_len_quiz,
    )


def quiz_window():
    return Window(
        Const('<u>Выбранные темы:</u>'),
        Format('<b>{name_themes}</b>'),
        Format('\nВсего вопросов: <b>{quiz_len}</b>'),
        Const(f'{texts.QUIZ_LEN_WARNING}', when=len_quiz_equal),
        Button(
            Const('🚀 Начать тест'),
            id='quiz_start',
            on_click=selected.on_quiz_step
        ),
        Back(Const(texts.BACK_BUTTON)),
        state=states.Quiz.quiz,
        getter=getters.get_quiz_params,
        parse_mode='HTML'
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
        state=states.Quiz.quiz_step,
        getter=getters.get_quiz_step,
        parse_mode='HTML'
    )


def quiz_result_window():
    return Window(
        Const('<u>Результат теста:</u>\n'),
        Format('🎉 Правильных ответов: {score} из {count}\n'),
        Format(
            text=('❗ Наибольшее количество ошибок ({errors_num}) '
                  'Вы совершили на вопросах по теме "{theme_name}"\n'),
            when='with_errors'
        ),
        Const(texts.QUIZ_REPORT_WARNING,  when='no_articles'),
        Format('🏆 Ваше место в рейтинге: {place} из {users} 👷🏼 ({move_sign}{move_num})'),
        keyboards.result_buttons(),
        state=states.Quiz.quiz_result,
        getter=getters.get_quiz_result,
        parse_mode='HTML'
    )


def quiz_report_window():
    return Window(
        Format('<u>Вопрос №{num}</u>'),
        Format('<b>{q_text}\n</b>'),
        Format('{ans_text}'),
        Const(texts.QUIZ_REPORT_LEGEND),
        Group(
            Select(
                Format('{item[2]} {item[0]} '),
                id='report_select_question',
                item_id_getter=lambda i: f'{i[0]}_{i[1]}',
                items='options',
                on_click=selected.on_quiz_report
            ),
            id='report',
            width=5,
        ),
        Back(Const(texts.BACK_BUTTON)),
        state=states.Quiz.quiz_report,
        getter=getters.get_quiz_report,
        parse_mode='HTML'
    )


def stats_window():
    return Window(
        Const('<u>Статистика прохождения тестов</u>\n'),
        Format('<b>{quiz_count}</b> - пройдено тестов'),
        Format('<b>{questions_count}</b> - задано вопросов'),
        Format('<b>{score}</b> - правильных ответов'),
        Format('\n🎖️ Рейтинг: {place} из {users}'),
        Button(
            Const('📉 Анализ ошибок'),
            id='error_analysis',
            on_click=selected.on_analysis,
            when='has_errors'
        ),
        Button(
            Const(texts.BACK_BUTTON),
            id='back_from_stats',
            on_click=selected.on_main_menu
        ),
        state=states.Quiz.stats,
        getter=getters.get_stats,
        parse_mode='HTML'
    )


def analysis_window():
    return Window(
        Const('<u>Распределение ошибок по темам:</u>\n'),
        Format('{text}'),
        Back(Const(texts.BACK_BUTTON)),
        state=states.Quiz.analysis,
        getter=getters.get_analysis_data,
        parse_mode='HTML'
    )


# проверка соответствия желания пользователя наличию вопросов в БД
def len_quiz_equal(data, widget, manager):
    ctx = manager.current_context()
    quiz_len_user = manager.find('quiz_len').get_checked()
    quiz_len_db = ctx.dialog_data['quiz_params']['len']
    return int(quiz_len_user) > int(quiz_len_db)
