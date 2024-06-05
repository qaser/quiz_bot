from aiogram_dialog import DialogManager
from utils.constants import DEPARTMENTS


async def get_departments(dialog_manager: DialogManager, **middleware_data):
    data = [(i, dep) for i, dep in enumerate(DEPARTMENTS)]
    return {'departments': data}
