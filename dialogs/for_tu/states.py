from aiogram.filters.state import State, StatesGroup


class Tu(StatesGroup):
    select_category = State()
    select_year = State()
    select_quarter = State()
    select_themes = State()
    select_date = State()
    save_plan = State()
    export_test = State()
    plan_review = State()
    quiz = State()
    quiz_step = State()
    quiz_result = State()
    quiz_reports = State()
    quiz_chosen_report = State()
