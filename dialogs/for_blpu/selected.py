from aiogram_dialog import DialogManager

from dialogs.for_blpu.states import Blpu
from utils.constants import DEPARTMENTS
from config.mongo_config import users


async def on_departments(callback, widget, manager: DialogManager, dep_id):
    context = manager.current_context()
    context.dialog_data.update(department=DEPARTMENTS[int(dep_id)])
    await manager.switch_to(Blpu.input_name)


async def save_username(callback, widget, manager: DialogManager, username):
    context = manager.current_context()
    department = context.dialog_data['department']
    user_id = manager.event.from_user.id
    users.update_one(
        {'user_id': user_id},
        {'$set': {'department': department, 'username': username}}
    )
    await manager.switch_to(Blpu.input_done)
