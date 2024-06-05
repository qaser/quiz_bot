from datetime import date
from aiogram_dialog import DialogManager
from bson.objectid import ObjectId

from dialogs.for_plans.states import Plans
from config.mongo_config import questions, themes, plans, scheduler_tu

QUIZ_LEN = 20


async def on_choose_category(callback, widget, manager: DialogManager):
    context = manager.current_context()
    context.dialog_data.update(category=widget.widget_id)
    await manager.switch_to(Plans.select_year)


async def on_year(callback, widget, manager: DialogManager):
    context = manager.current_context()
    context.dialog_data.update(year=widget.text.text)
    await manager.switch_to(Plans.select_quarter)


async def on_quarter(callback, widget, manager: DialogManager):
    context = manager.current_context()
    context.dialog_data.update(quarter=widget.text.text)
    if context.dialog_data['category'] == 'new_plan':
        await get_themes(manager)
        await manager.switch_to(Plans.select_themes)
    elif context.dialog_data['category'] == 'show_plan':
        await manager.switch_to(Plans.plan_review)
    elif context.dialog_data['category'] == 'export_test':
        await manager.switch_to(Plans.export_test)


async def get_themes(manager: DialogManager):
    context = manager.current_context()
    queryset = questions.distinct('theme')
    data = []
    for code in queryset:
        res = {}
        name = themes.find_one({'code': code})['name']
        res['code'] = code
        res['name'] = name
        data.append(res)
    context.dialog_data.update(themes=data)
    context.dialog_data.update(themes_count=0)


async def on_themes_done(callback, widget, manager: DialogManager):
    ctx = manager.current_context()
    widget = manager.find('s_themes')
    q_ids = get_questions(widget.get_checked())
    plan = plans.find_one_and_update(
        {
            'department': ctx.dialog_data['department'],
            'year': int(ctx.dialog_data['year']),
            'quarter': int(ctx.dialog_data['quarter'])
        },
        {'$set':
            {
                'themes': widget.get_checked(),
                'owner': manager.event.from_user.id,
                'questions': q_ids,
            }
        },
        upsert=True,
        return_document=True,
    )
    ctx.dialog_data.update(plan_id=str(plan['_id']))
    ctx.dialog_data.update(period_start='')
    ctx.dialog_data.update(period_end='')
    await manager.switch_to(Plans.select_date)


def get_questions(themes_list):
    pipeline = [
        {'$match': {
            'theme': {'$in': themes_list},
            'is_active': True,
            'multiple': False
        }},
        {'$sample': {'size': QUIZ_LEN}},
        {'$group': {
            '_id': ObjectId(),
            'q_ids': {'$push': '$_id'},
        }},
    ]
    return list(questions.aggregate(pipeline))[0]['q_ids']


async def on_select_date(callback, widget, manager, clicked_date):
    ctx = manager.current_context()
    period = clicked_date.strftime('%d.%m.%Y')
    period_start = ctx.dialog_data['period_start']
    if period_start == '':
        ctx.dialog_data.update(period_start=period)
        await manager.switch_to(Plans.select_date)
    else:
        ctx.dialog_data.update(period_end=period)
        save_plan_in_scheduler(manager)
        await manager.switch_to(Plans.save_plan)



def save_plan_in_scheduler(manager: DialogManager):
    ctx = manager.current_context()
    periods = [
        (ctx.dialog_data['period_start'], 'input'),
        (ctx.dialog_data['period_end'], 'output')
    ]
    for period in periods:
        scheduler_tu.insert_one(
            {
                'date': period[0],
                'quiz_type': period[1],
                # 'time': '10:00',
                'type': 'quiz_plan',
                'event_id': ObjectId(ctx.dialog_data['plan_id']),
            }
        )
