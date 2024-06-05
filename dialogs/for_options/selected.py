from aiogram_dialog import DialogManager, StartMode

from dialogs.for_options.states import Options
from config.mongo_config import users, results


async def on_main_menu(callback, widget, manager: DialogManager):
    await manager.start(Options.select_category, mode=StartMode.RESET_STACK)


async def on_conditions(callback, widget, manager: DialogManager):
    await manager.switch_to(Options.conditions)


# async def on_subscribe(callback, widget, manager: DialogManager):
#     await manager.switch_to(Options.subscribe)


async def on_delete(callback, widget, manager: DialogManager):
    await manager.switch_to(Options.delete_user)


# async def on_subscribe_change(callback, widget, manager: DialogManager):
#     user_id = manager.event.from_user.id
#     user_data = users.find_one({'user_id': user_id})
#     silent_mode = user_data['silent_mode']
#     silent_mode = not silent_mode
#     users.update_one(
#         {'user_id': user_id},
#         {'$set': {'silent_mode': silent_mode}}
#     )
#     await manager.switch_to(Options.subscribe)


async def on_delete_user(callback, widget, manager: DialogManager):
    user_id = manager.event.from_user.id
    users.delete_one({'user_id': user_id})
    results.delete_one({'user_id': user_id})
    try:
        await manager.done()
        await callback.message.delete()
    except:
        pass
