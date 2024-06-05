from aiogram.filters.state import State, StatesGroup


class Options(StatesGroup):
    select_category = State()
    conditions = State()
    # subscribe = State()
    delete_user = State()
