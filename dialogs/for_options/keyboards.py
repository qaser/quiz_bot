from aiogram_dialog.widgets.kbd import Button, Column
from aiogram_dialog.widgets.text import Const, Format

import utils.constants as texts

from . import selected


def category_buttons():
    return Column(
        Button(
            Const('📝 Пользовательское соглашение'),
            id='conditions',
            on_click=selected.on_conditions
        ),
        # Button(
        #     Const('📣 Уведомления'),
        #     id='subscribe',
        #     on_click=selected.on_subscribe
        # ),
        # Button(
        #     Const('🏅 Мои достижения'),
        #     id='records',
        #     on_click=selected.on_records
        # ),
        Button(
            Const('❌ Удалить аккаунт'),
            id='user_delete',
            on_click=selected.on_delete
        ),
        # Button(
        #     Const('💬 Обратная связь'),
        #     id='feedback',
        #     on_click=selected.feedback
        # ),
    )


def subscribe_buttons():
    return Column(
        Button(
            Format('{active} "тихий режим"'),
            id='subscribe_change',
            on_click=selected.on_subscribe_change
        ),
        Button(
            Const(texts.BACK_BUTTON),
            id='back_from_subs',
            on_click=selected.on_main_menu
        ),
    )


def delete_user_buttons():
    return Column(
        Button(
            Const('Удалить аккаунт'),
            id='delete_user',
            on_click=selected.on_delete_user
        ),
        Button(
            Const(texts.BACK_BUTTON),
            id='back_from_user',
            on_click=selected.on_main_menu
        ),
    )
