from aiogram_dialog.widgets.kbd import Select, Column
from aiogram_dialog.widgets.text import Format

def department_buttons(on_click):
    return Column(
        Select(
            Format('{item[1]}'),
            id='departments',
            item_id_getter=lambda x: x[0],
            items='departments',
            on_click=on_click,
        )
    )
