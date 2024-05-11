from aiogram_dialog import DialogManager

from dialogs.for_terms.states import Terms


async def on_chosen_themes(callback, widget, manager: DialogManager, theme_code):
    context = manager.current_context()
    context.dialog_data.update(theme_code=theme_code)
    await manager.switch_to(Terms.select_terms)


async def on_chosen_terms(callback, widget, manager: DialogManager, term_id):
    context = manager.current_context()
    context.dialog_data.update(term_id=term_id)
    await manager.switch_to(Terms.description)
