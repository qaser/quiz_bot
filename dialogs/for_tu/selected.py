import datetime as dt
import random
from collections import Counter

from aiogram_dialog import DialogManager
from bson.objectid import ObjectId

from config.mongo_config import (answers, docs, plans, questions, results_tu,
                                 scheduler_tu, themes)
from dialogs.for_tu.states import Tu
from utils.utils import calc_grade

QUIZ_LEN = 20


async def on_choose_category(callback, widget, manager: DialogManager):
    context = manager.current_context()
    context.dialog_data.update(category=widget.widget_id)
    await manager.switch_to(Tu.select_year)


async def on_year(callback, widget, manager: DialogManager):
    context = manager.current_context()
    context.dialog_data.update(year=widget.text.text)
    await manager.switch_to(Tu.select_quarter)


async def on_quarter(callback, widget, manager: DialogManager):
    context = manager.current_context()
    context.dialog_data.update(quarter=widget.text.text)
    if context.dialog_data['category'] == 'new_plan':
        await get_themes(manager)
        await manager.switch_to(Tu.select_themes)
    elif context.dialog_data['category'] == 'show_plan':
        await manager.switch_to(Tu.plan_review)
    elif context.dialog_data['category'] == 'export_test':
        await manager.switch_to(Tu.export_test)


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
    await manager.switch_to(Tu.select_date)


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
            'q_ids': {'$push': {"$toString": "$_id"}},
        }},
    ]
    return list(questions.aggregate(pipeline))[0]['q_ids']


async def on_select_date(callback, widget, manager, clicked_date):
    ctx = manager.current_context()
    period = clicked_date.strftime('%d.%m.%Y')
    period_start = ctx.dialog_data['period_start']
    if period_start == '':
        ctx.dialog_data.update(period_start=period)
        await manager.switch_to(Tu.select_date)
    else:
        ctx.dialog_data.update(period_end=period)
        save_plan_in_scheduler(manager)
        await manager.switch_to(Tu.save_plan)



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


async def on_quiz_step(callback, widget, manager: DialogManager):
    context = manager.current_context()
    quiz_count = context.dialog_data['quiz_count']  # счетчик вопросов (начинается от 0)
    quiz_step = context.dialog_data.get('quiz_step', None)
    if quiz_step is not None:
        is_multiple = quiz_step['multiple']
        user_answer = manager.find('user_answers').get_checked()
        # блок проверки ответов пользователя
        user_result = context.dialog_data['user_result']
        user_count = user_result['count']
        ans_correct = context.dialog_data['user_result']['answers_correct']
        if is_multiple and user_answer is not None:  # если вопрос с несколькими ответами
            q_id = context.dialog_data['quiz_step']['q_id']
            correct_ans = list(answers.find({'q_id': ObjectId(q_id), 'is_correct': True}))
            correct_ans_ids = [str(ans['_id']) for ans in correct_ans]
            if Counter(correct_ans_ids) == Counter(user_answer):
                user_count+=1
                context.dialog_data['user_result']['count'] = user_count
            else:
                pass  # добавить обработку неправильного ответа
            await manager.find('user_answers').reset_checked()
        elif is_multiple is False and user_answer is not None:
            ans_check = answers.find_one({'_id': ObjectId(user_answer)})
            if ans_check['is_correct']:
                user_count+=1
                context.dialog_data['user_result']['count'] = user_count
                ans_correct.append('🟢')
                context.dialog_data['user_result'].update(answers_correct=ans_correct)
            else:  # если юзер ответил неправильно на вопрос
                theme_list = user_result['errors_themes']
                theme_list.append(quiz_step['theme'])
                context.dialog_data['user_result']['errors_themes'] = theme_list
                ans_correct.append('🔴')
                context.dialog_data['user_result'].update(answers_correct=ans_correct)
            del manager.current_context().widget_data['user_answers']
        elif user_answer is None:
            ans_correct.append('⚪')
            context.dialog_data['user_result'].update(answers_correct=ans_correct)
        answer_list = user_result['answers']
        answer_list.append(user_answer)
        context.dialog_data['user_result']['answers'] = answer_list
    quiz_params = context.dialog_data['quiz_params']
    quiz_len = quiz_params['len']  # сколько всего вопросов
    if quiz_count == quiz_len:  # завершение теста, сохранение результата юзера
        save_quiz_result(manager)
        await manager.switch_to(Tu.quiz_result)
    else:
        await prepare_question(manager, quiz_count)
        quiz_count+=1
        context.dialog_data.update(quiz_count=quiz_count)
        await manager.switch_to(Tu.quiz_step)


async def prepare_question(dialog_manager: DialogManager, q_id):
    ctx = dialog_manager.current_context()
    quiz_params = ctx.dialog_data['quiz_params']
    question = questions.find_one({'_id': ObjectId(quiz_params['q_ids'][q_id]), 'is_active': True})
    q_answers = list(answers.find({'q_id': question['_id'], 'is_active': True}))
    doc_instance = docs.find_one({'_id': question['doc']})
    if doc_instance is not None:
        doc_allows = True
        doc_name = doc_instance['name']
    else:
        doc_name = None
        doc_allows = False
    if question['random_allows'] is True:
        random.shuffle(q_answers)
    ans_text = ''
    options = []
    for id, ans in enumerate(q_answers):
        text = ans['text']
        ans_id = str(ans['_id'])
        ans_text = f'{ans_text}<b>{id+1}</b>. {text}\n'
        options.append((id+1, ans_id))
    quiz_step = {
        'q_id': str(question['_id']),
        'count': int(q_id)+1,  # счетчик вопросов
        'len': quiz_params['len'],
        'text': question['text'],
        'answers': ans_text,
        'options': options,
        'multiple': question['multiple'],
        'doc': doc_name,
        'doc_allows': doc_allows,
        'theme': question['theme'],
    }
    ctx.dialog_data.update(quiz_step=quiz_step)


def save_quiz_result(manager: DialogManager):
    context = manager.current_context()
    user_id = manager.event.from_user.id
    plan_id = context.dialog_data['plan_id']
    quiz_type = context.dialog_data['quiz_type']
    quiz_len = context.dialog_data['quiz_params']['len']
    user_result = context.dialog_data['user_result']
    plan_tu = plans.find_one({'_id': ObjectId(plan_id)})
    grade = calc_grade(user_result['count'], quiz_len)
    context.dialog_data.update(grade=grade)
    results_tu.update_one(
        {
            'user_id': user_id,
            'year': plan_tu['year'],
            'quarter': plan_tu['quarter'],
            'quiz_type': quiz_type
        },
        {'$set': {
            'done': True,
            'date': dt.datetime.now(),
            'grade': grade,
            'quiz_results': user_result
        }},
        upsert=True
    )


async def on_quiz_reports(callback, widget, manager: DialogManager):
    context = manager.current_context()

    await manager.switch_to(Tu.quiz_reports)


async def on_chosen_quiz_report(callback, widget, manager: DialogManager, data=None):
    context = manager.current_context()
    if widget.widget_id == 'input_result':
        user_result = context.dialog_data['input_result']
        context.dialog_data.update(user_result=user_result)
    elif widget.widget_id == 'output_result':
        user_result = context.dialog_data['output_result']
        context.dialog_data.update(user_result=user_result)
    if data is None:
        q_id = context.dialog_data['quiz_params']['q_ids'][0]
        ans_id = 1
    else:
        ans_id, q_id = data.split('_')
    context.dialog_data.update(report_q_id=q_id)
    context.dialog_data.update(report_ans_id=int(ans_id)-1)
    await manager.switch_to(Tu.quiz_chosen_report)
