import operator

from aiogram_dialog.widgets.kbd import Select, Column
from aiogram_dialog.widgets.text import Format

def themes_buttons(on_click):
    return Column(
        Select(
            Format('{item[0]}'),
            id='column_themes',
            item_id_getter=operator.itemgetter(1),
            items='themes',
            on_click=on_click,
        )
    )


def terms_buttons(on_click):
    return Column(
        Select(
            Format('{item[0]}'),
            id='column_terms',
            item_id_getter=operator.itemgetter(1),
            items='terms',
            on_click=on_click,
        )
    )
