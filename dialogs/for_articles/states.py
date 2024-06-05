from aiogram.filters.state import State, StatesGroup


class Articles(StatesGroup):
    select_category = State()
    select_themes = State()
    select_tags = State()
    random_article = State()
    articles_info = State()
