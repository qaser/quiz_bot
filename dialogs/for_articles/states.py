from aiogram.filters.state import State, StatesGroup


class Articles(StatesGroup):
    select_category = State()
    select_themes = State()
    select_articles = State()
    article_url = State()
    article_rules = State()
    input_article_name = State()
    input_article_url = State()
    random_article = State()
    article_save_done = State()
