from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Back, Button, Cancel
from aiogram_dialog.widgets.text import Const, Format

from dialogs.for_terms.states import Terms

from . import getters, keyboards, selected


async def on_click(callback, button, dialog_manager):
    try:
        await dialog_manager.done()
        await callback.message.delete()
    except:
        pass


def themes_window():
    return Window(
        Const('Термины и определения.\nВыберите тему:'),
        keyboards.themes_buttons(selected.on_chosen_themes),
        Cancel(Const('🔚 Выход'), on_click=on_click),
        state=Terms.select_themes,
        getter=getters.get_themes
    )


def terms_window():
    return Window(
        Const('Выберите термин:'),
        keyboards.terms_buttons(selected.on_chosen_terms),
        Back(Const('🔙 Назад')),
        state=Terms.select_terms,
        getter=getters.get_terms
    )


def description_window():
    return Window(
        Format('{term}'),
        Back(Const('🔙 Назад')),
        state=Terms.description,
        getter=getters.get_description,
    )
