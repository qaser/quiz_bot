from aiogram.filters.state import State, StatesGroup


class Blpu(StatesGroup):
    select_department = State()
    input_name = State()
    input_done = State()
