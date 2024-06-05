from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Cancel, Back
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput

from . import keyboards, getters, selected
from dialogs.for_blpu.states import Blpu


async def on_click(callback, button, dialog_manager):
    try:
        await dialog_manager.done()
        await callback.message.delete()
    except:
        pass


def department_window():
    return Window(
        Const('Выберите службу'),
        keyboards.department_buttons(selected.on_departments),
        Cancel(Const('🔚 Отмена'), on_click=on_click),
        state=Blpu.select_department,
        getter=getters.get_departments
    )


def input_name_window():
    return Window(
        Const('Введите свои данные в формате:\n<i>Фамилия И.О.</i>'),
        TextInput(
            id='user_name',
            on_success=selected.save_username,
        ),
        Back(Const('🔙 Назад')),
        state=Blpu.input_name,
        parse_mode='HTML'
    )


def done_window():
    return Window(
        Const('Данные сохранены'),
        Cancel(Const('🔚 Выход'), on_click=on_click),
        state=Blpu.input_done,
    )
