from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode

from dialogs.for_terms import windows
from dialogs.for_terms.states import Terms

router = Router()
dialog =  Dialog(
    windows.themes_window(),
    windows.terms_window(),
    windows.description_window(),
)


@router.message(Command('terms'))
async def terms_request(message: Message, dialog_manager: DialogManager):
    await message.delete()
    # Important: always set `mode=StartMode.RESET_STACK` you don't want to stack dialogs
    await dialog_manager.start(Terms.select_themes, mode=StartMode.RESET_STACK)
