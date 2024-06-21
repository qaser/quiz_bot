from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode

from dialogs.for_options import windows
from dialogs.for_options.states import Options

router = Router()
dialog =  Dialog(
    windows.options_main_window(),
    windows.conditions_window(),
    # windows.subscribe_window(),
    windows.delete_user_window(),
)


@router.message(Command('options'))
async def options(message: Message, dialog_manager: DialogManager):
    await message.delete()
    # Important: always set `mode=StartMode.RESET_STACK` you don't want to stack dialogs
    await dialog_manager.start(Options.select_category, mode=StartMode.RESET_STACK)
