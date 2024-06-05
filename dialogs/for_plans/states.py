from aiogram.filters.state import State, StatesGroup


class Plans(StatesGroup):
    select_category = State()
    select_year = State()
    select_quarter = State()
    select_themes = State()
    select_date = State()
    save_plan = State()
    export_test = State()
    plan_review = State()
