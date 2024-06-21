import random
import datetime as dt
from collections import Counter

from aiogram_dialog import DialogManager, StartMode
from bson.objectid import ObjectId

from config.mongo_config import answers, docs, questions, results, themes, plans, results_tu
from utils.utils import calc_grade

from . import states


async def on_main_menu(callback, widget, manager: DialogManager):
    context = manager.current_context()
    if context.dialog_data['category'] == 'tu_quiz':
        try:
            await manager.done()
            await callback.message.delete()
        except:
            pass
    else:
        await manager.start(states.Quiz.select_category, mode=StartMode.RESET_STACK)


async def on_choose_themes(callback, widget, manager: DialogManager):
    context = manager.current_context()
    queryset = questions.distinct('theme')
    data = []
    for code in queryset:
        res = {}
        name = themes.find_one({'code': code})['name']
        res['code'] = code
        res['name'] = name
        data.append(res)
    context.dialog_data.update(category='quiz')
    context.dialog_data.update(themes=data)
    context.dialog_data.update(themes_count=0)
    await manager.switch_to(states.Quiz.select_themes)


async def on_themes_done(callback, widget, manager: DialogManager):
    context = manager.current_context()
    widget = manager.find('s_themes')
    context.dialog_data.update(selected_themes=widget.get_checked())
    await manager.switch_to(states.Quiz.select_len_quiz)


async def on_quiz_params(callback, widget, manager: DialogManager):
    quiz_len = manager.find('quiz_len').get_checked()
    if quiz_len is None:
        await callback.answer('Выберите количество вопросов', show_alert=True)
    else:
        ctx = manager.current_context()
        ctx.dialog_data.update(quiz_len=quiz_len)
        await manager.switch_to(states.Quiz.quiz)


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
                pass  # добавить обработку не правильного ответа
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
    if quiz_count == quiz_len:  # завершение теста, сохранение статистики юзера
        if context.dialog_data['category'] == 'tu_quiz':
            save_tu_quiz_result(manager)
            await manager.switch_to(states.Quiz.tu_quiz_result)
        else:
            user_stats_update(manager)
            await manager.switch_to(states.Quiz.quiz_result)
    else:
        await prepare_question(manager, quiz_count)
        quiz_count+=1
        context.dialog_data.update(quiz_count=quiz_count)
        await manager.switch_to(states.Quiz.quiz_step)


def user_stats_update(manager: DialogManager):
    context = manager.current_context()
    user_id = manager.event.from_user.id
    res = results.find_one({'user_id': user_id})
    questions_count = context.dialog_data['quiz_params']['len']
    score = context.dialog_data['user_result']['count']
    errors_themes = dict(Counter(context.dialog_data['user_result']['errors_themes']))
    if res is None:
        results.insert_one(
            {
                'user_id': user_id,
                'score': score,
                'questions_count': questions_count,
                'quiz_count': 1,
                'rating': 0,
                'place': 0,
                'errors_themes': errors_themes,
            }
        )
    else:
        q_count = questions_count + res['questions_count']
        user_score = score + res['score']
        quiz_count = res['quiz_count'] + 1
        rating = int((user_score / q_count) * 100000) + quiz_count
        new_place = results.count_documents({'rating': {'$gt': rating}})
        new_place = 1 if new_place == 0 else new_place
        old_place = res['place']
        move = old_place - new_place
        move_num = f'+{move}' if move > 0 else str(move)
        move_sign = '🔺' if move > 0 else '🔻'
        context.dialog_data.update(place=new_place)
        context.dialog_data.update(move_num=move_num)
        context.dialog_data.update(move_sign=move_sign)
        results.update_one(
            {'user_id': user_id},
            {'$set': {
                'score': user_score,
                'questions_count': q_count,
                'quiz_count': quiz_count,
                'rating': rating,
                'place': new_place,
                'errors_themes': {**errors_themes, **res['errors_themes']}
            }},
            upsert=False
        )


def save_tu_quiz_result(manager: DialogManager):
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


async def on_quiz_report(callback, widget, manager: DialogManager, data=None):
    context = manager.current_context()
    if data is None:
        q_id = context.dialog_data['quiz_params']['q_ids'][0]
        ans_id = 1
    else:
        ans_id, q_id = data.split('_')
    context.dialog_data.update(report_q_id=q_id)
    context.dialog_data.update(report_ans_id=int(ans_id)-1)
    await manager.switch_to(states.Quiz.quiz_report)


async def on_stats(callback, widget, manager: DialogManager):
    context = manager.current_context()
    context.dialog_data.update(category='stats')
    await manager.switch_to(states.Quiz.stats)


async def on_analysis(callback, widget, manager: DialogManager):
    await manager.switch_to(states.Quiz.analysis)


async def on_quiz_guideline(callback, widget, manager: DialogManager):
    await manager.switch_to(states.Quiz.articles)


async def on_adding_questions(callback, widget, manager: DialogManager):
    # context = manager.current_context()
    # context.dialog_data.update(category='stats')
    print('Добавление вопросов')
    # await manager.switch_to(states.Quiz.stats)
