from aiogram_dialog import DialogManager

from dialogs.for_articles.states import Articles


async def on_chosen_themes(callback, widget, manager: DialogManager):
    context = manager.current_context()
    await manager.switch_to(Articles.select_themes)


async def on_random_article(callback, widget, manager: DialogManager):
    await manager.switch_to(Articles.random_article)


async def on_themes_done(callback, widget, manager: DialogManager):
    pass
