from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Back, Cancel
from aiogram_dialog.widgets.text import Const, Format

import utils.constants as texts
from dialogs.for_options.states import Options

from . import getters, keyboards

SUBSCRIBE_TEXT = ('Бот может рассылать уведомления об обновлениях приложения.\n'
                  'Если Вы не хотите получать уведомления, то включите "тихий режим"')
DELETE_TEXT = ('Удалив аккаунт Вы потеряете свой прогресс и рейтинг среди '
               'пользователей. При необходимости Вы сможете повторно зарегистрироваться')


async def on_click(callback, button, dialog_manager):
    try:
        await dialog_manager.done()
        await callback.message.delete()
    except:
        pass


def options_main_window():
    return Window(
        Const('Настройки приложения.\nВыберите категорию:'),
        keyboards.category_buttons(),
        Cancel(Const('🔚 Выход'), on_click=on_click),
        state=Options.select_category,
    )


def conditions_window():
    return Window(
        Const('<b>Пользовательское соглашение</b>'),
        Format('Версия от {date}г.'),
        Format('{text}'),
        Back(Const(texts.BACK_BUTTON)),
        state=Options.conditions,
        getter=getters.get_conditions,
    )


def subscribe_window():
    return Window(
        Const('<b>Настройка рассылки</b>\n'),
        Const(SUBSCRIBE_TEXT),
        Format('На данный момент у Вас <u>{status}</u> "тихий режим"'),
        keyboards.subscribe_buttons(),
        state=Options.subscribe,
        getter=getters.get_subscribe,

    )


def delete_user_window():
    return Window(
        Const('<b>Удаление аккаунта</b>\n'),
        Const(DELETE_TEXT),
        keyboards.delete_user_buttons(),
        state=Options.delete_user,
    )
