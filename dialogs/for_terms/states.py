from aiogram.filters.state import State, StatesGroup


class Terms(StatesGroup):
    select_themes = State()
    select_terms = State()
    description = State()
