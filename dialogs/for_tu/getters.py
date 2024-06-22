from collections import Counter

from aiogram_dialog import DialogManager
from bson.objectid import ObjectId

from config.mongo_config import (answers, plans, questions, results_tu, themes,
                                 users)
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


async def get_quiz_params(dialog_manager: DialogManager, **middleware_data):
    ctx = dialog_manager.current_context()
    plan_id = dialog_manager.start_data['plan_id']
    quiz_type = dialog_manager.start_data['quiz_type']
    plan_tu = plans.find_one({'_id': ObjectId(plan_id)})
    quiz_params = {'q_ids': plan_tu['questions'], 'len': len(plan_tu['questions'])}
    selected_themes = plan_tu['themes']
    ctx.dialog_data.update(selected_themes=selected_themes)
    ctx.dialog_data.update(quiz_params=quiz_params)
    ctx.dialog_data.update(quiz_type=quiz_type)
    ctx.dialog_data.update(plan_id=plan_id)
    ctx.dialog_data.update(quiz_count=0)
    ctx.dialog_data.update(user_result={})  # данные о результате пользователя
    ctx.dialog_data['user_result']['count'] = 0
    ctx.dialog_data['user_result']['answers'] = []
    ctx.dialog_data['user_result']['answers_correct'] = []
    ctx.dialog_data['user_result']['errors_themes'] = []
    name_themes = ',\n'.join([themes.find_one({'code': code})['name'] for code in selected_themes])
    return {'name_themes': name_themes, 'quiz_len': quiz_params['len']}


async def get_quiz_step(dialog_manager: DialogManager, **middleware_data):
    ctx = dialog_manager.current_context()
    quiz_step = ctx.dialog_data['quiz_step']
    return quiz_step


async def get_quiz_result(dialog_manager: DialogManager, **middleware_data):
    context = dialog_manager.current_context()
    questions_count = context.dialog_data['quiz_params']['len']
    score = context.dialog_data['user_result']['count']
    errors_themes = Counter(context.dialog_data['user_result']['errors_themes']).most_common(1)
    if len(errors_themes) > 0:
        theme_code, errors_num = errors_themes[0]
        theme_name = themes.find_one({'code': theme_code})['name']
        with_errors = True
    else:
        theme_name = ''
        errors_num = ''
        with_errors = False
    grade = context.dialog_data['grade']
    quiz_type = context.dialog_data['quiz_type']
    report_access = True if quiz_type == 'output' else False
    data = {
        'count': questions_count,
        'score': score,
        'errors_num': errors_num,
        'theme_name': theme_name,
        'with_errors': with_errors,
        'grade': grade,
        'report_access': report_access
    }
    return data


async def get_quiz_reports(dialog_manager: DialogManager, **middleware_data):
    context = dialog_manager.current_context()
    user_id = dialog_manager.event.from_user.id
    plan_id = context.dialog_data['plan_id']
    plan_tu = plans.find_one({'_id': ObjectId(plan_id)})
    y = plan_tu['year']
    q = plan_tu['quarter']
    input_result = results_tu.find_one({
        'user_id': user_id,
        'quarter': q,
        'year': y,
        'quiz_type': 'input',
        'done': True
    })
    if input_result is not None:
        input_res = input_result['quiz_results']
        input_grade = input_result['grade']
        input_ans = input_res['count']
        input_quiz = len(input_res['answers'])
        input_date = input_result['date'].strftime('%d.%m.%Y')
        input_access = True
        context.dialog_data.update(input_result=input_res)
    output_result = results_tu.find_one({
        'user_id': user_id,
        'quarter': q,
        'year': y,
        'quiz_type': 'output',
        'done': True
    })
    if output_result is not None:
        output_res = output_result['quiz_results']
        output_grade = output_result['grade']
        output_ans = output_res['count']
        output_quiz = len(output_res['answers'])
        output_date = output_result['date'].strftime('%d.%m.%Y')
        output_access = True
        context.dialog_data.update(output_result=output_res)
    data = {
        'y': y,
        'q': q,
        'input_grade': input_grade if input_result is not None else '',
        'input_date': input_date if input_result is not None else '',
        'input_ans': input_ans if input_result is not None else '',
        'input_quiz': input_quiz if input_result is not None else '',
        'input_access': input_access if input_result is not None else False,
        'output_grade': output_grade if output_result is not None else '',
        'output_date': output_date if output_result is not None else '',
        'output_ans': output_ans if output_result is not None else '',
        'output_quiz': output_quiz if output_result is not None else '',
        'output_access': output_access if output_result is not None else False,
    }
    return data


async def get_chosen_quiz_report(dialog_manager: DialogManager, **middleware_data):
    context = dialog_manager.current_context()
    q_id = context.dialog_data['report_q_id']
    ans_id = context.dialog_data['report_ans_id']
    current_q = questions.find_one({'_id': ObjectId(q_id)})
    current_ans = list(answers.find({'q_id': ObjectId(q_id), 'is_active': True}))
    user_ans_id = context.dialog_data['user_result']['answers'][ans_id]
    ans_correct = context.dialog_data['user_result']['answers_correct']
    qs = context.dialog_data['quiz_params']['q_ids']
    ans_text = ''
    for id, ans in enumerate(current_ans):
        mark = '🔵' if str(ans['_id']) == user_ans_id else '⚪'
        text = f'<u>{ans["text"]}</u>' if ans['is_correct'] else ans['text']
        ans_text = f'{ans_text}{mark} {id+1}. {text}\n'
    data = {
        'num': int(ans_id) + 1,
        'q_text': current_q['text'],
        'ans_text': ans_text,
        'options': [(num+1, id, ans_correct[num]) for num, id in enumerate(qs)],
    }
    return data
