from aiogram_dialog import DialogManager

from config.mongo_config import conditions, users


async def get_conditions(dialog_manager: DialogManager, **middleware_data):
    condition = conditions.find({}).sort({'release_date': -1}).limit(1)[0]
    date = condition['release_date'].strftime('%d.%m.%Y')
    text = condition['text']
    return {'date': date, 'text': text}


# async def get_subscribe(dialog_manager: DialogManager, **middleware_data):
#     user_id = dialog_manager.event.from_user.id
#     user_data = users.find_one({'user_id': user_id})
#     silent_mode = user_data['silent_mode']
#     status = 'выключен' if silent_mode == False else 'включен'
#     active = '🔕 Включить' if silent_mode == False else '🔔 Выключить'
#     return {'status': status, 'active': active}
