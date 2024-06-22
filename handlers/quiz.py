from aiogram import F, Router
from aiogram.exceptions import AiogramError
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, StartMode

from dialogs.for_quiz import windows
from dialogs.for_quiz.states import Quiz

router = Router()
dialog =  Dialog(
    windows.quiz_main_window(),
    windows.themes_window(),
    windows.len_quiz_window(),
    windows.quiz_window(),
    windows.quiz_step_window(),
    windows.quiz_result_window(),
    windows.quiz_report_window(),
    windows.stats_window(),
    windows.analysis_window(),
    windows.articles_window(),
)


@router.message(Command('quiz'))
async def quiz_request(message: Message, dialog_manager: DialogManager):
    await message.delete()
    # Important: always set `mode=StartMode.RESET_STACK` you don't want to stack dialogs
    await dialog_manager.start(
        Quiz.select_category,
        data={'category': 'quiz'},
        mode=StartMode.RESET_STACK
    )
