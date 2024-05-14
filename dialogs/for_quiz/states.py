from aiogram.filters.state import State, StatesGroup


class Quiz(StatesGroup):
    select_category = State()
    stats = State()
    analysis = State()
    select_themes = State()
    select_len_quiz = State()
    quiz = State()
    quiz_step = State()
    quiz_result = State()
    quiz_report = State()
    articles = State()
