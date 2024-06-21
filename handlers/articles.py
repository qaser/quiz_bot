from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode

from dialogs.for_articles import windows
from dialogs.for_articles.states import Articles

router = Router()
dialog =  Dialog(
    windows.category_window(),
    windows.random_article_window(),
    windows.select_themes_window(),
    # windows.select_tags_window(),
    # windows.select_article_window(),
    # windows.new_article_window(),
)


@router.message(Command('articles'))
async def articles_handler(message: Message, dialog_manager: DialogManager):
    # await message.delete()
    # Important: always set `mode=StartMode.RESET_STACK` you don't want to stack dialogs
    await dialog_manager.start(Articles.select_category, mode=StartMode.RESET_STACK)
