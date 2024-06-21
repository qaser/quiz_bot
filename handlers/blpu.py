from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode

from dialogs.for_blpu import windows
from dialogs.for_blpu.states import Blpu

router = Router()
dialog =  Dialog(
    windows.department_window(),
    windows.input_name_window(),
    windows.done_window(),
)


@router.message(Command('blpu'))
async def blpu_request(message: Message, dialog_manager: DialogManager):
    await message.delete()
    # Important: always set `mode=StartMode.RESET_STACK` you don't want to stack dialogs
    await dialog_manager.start(Blpu.select_department, mode=StartMode.RESET_STACK)
