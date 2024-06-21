from aiogram_dialog import DialogManager
from bson.objectid import ObjectId

from config.mongo_config import plans, users
from dialogs.for_tu.states import Tu
from utils.constants import MONTHS_NAMES


async def get_themes(dialog_manager: DialogManager, **middleware_data):
    ctx = dialog_manager.current_context()
    widget = dialog_manager.find('s_themes')
    themes_list = ctx.dialog_data['themes']
    themes_count = len(widget.get_checked())
    user_warn = True if themes_count == 15 else False
    chosen_one = False if themes_count == 0 else True
    dep = users.find_one({'user_id': dialog_manager.event.from_user.id}).get('department')
    if dep:
        plan = plans.find_one(
            {
                'department': dep,
                'year': ctx.dialog_data['year'],
                'quarter': ctx.dialog_data['quarter']
            }
        )
        ctx.dialog_data.update(department=dep)
        plan_it = True if plan else False
    else:
        plan_it = False
    return {
        'themes': themes_list,
        'themes_count': themes_count,
        'warning': user_warn,
        'plan_it': plan_it,
        'chosen_one': chosen_one,
    }


async def get_plan_params(dialog_manager: DialogManager, **middleware_data):
    ctx = dialog_manager.current_context()
    period_start = ctx.dialog_data.get('period_start')
    period = 'начале' if period_start == '' else 'конце'
    q = int(ctx.dialog_data['quarter'])
    y = ctx.dialog_data['year']
    m = str((q * 3) if period == 'конце' else ((q * 3) - 2))
    return {
        'y': y,
        'q': q,
        'm': MONTHS_NAMES[m],
        'period': period,
    }
