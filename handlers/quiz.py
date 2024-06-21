from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, StartMode
from aiogram.exceptions import AiogramError
from bson.objectid import ObjectId

from dialogs.for_quiz import windows
from dialogs.for_quiz.states import Quiz
from config.mongo_config import plans

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
    windows.tu_quiz_window(),
    windows.tu_quiz_result_window()
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


@router.callback_query(F.data.startswith('tu_'))
async def get_test_quarter(callback: CallbackQuery, dialog_manager: DialogManager):
    _, plan_id, quiz_type = callback.data.split('_')
    try:
        await callback.message.delete()
    except AiogramError:
        pass
        # сделать проверку на прохождение пользователем этого теста
    await dialog_manager.start(
        Quiz.tu_quiz,
        data={'plan_id':plan_id, 'quiz_type': quiz_type, 'category': 'tu_quiz'},
        mode=StartMode.NEW_STACK
    )
