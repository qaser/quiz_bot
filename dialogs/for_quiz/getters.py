from collections import Counter

from aiogram_dialog import DialogManager
from bson.objectid import ObjectId

from config.mongo_config import (answers, articles, questions, results, themes,
                                 users, plans)


async def get_themes(dialog_manager: DialogManager, **middleware_data):
    ctx = dialog_manager.current_context()
    widget = dialog_manager.find('s_themes')
    themes_list = ctx.dialog_data['themes']
    themes_count = len(widget.get_checked())
    user_warn = True if themes_count == 5 else False
    return {
        'themes': themes_list,
        'themes_count': themes_count,
        'warning': user_warn
    }


async def get_quiz_params(dialog_manager: DialogManager, **middleware_data):
    ctx = dialog_manager.current_context()
    category = dialog_manager.start_data.get('category')
    if category == 'tu_quiz':
        ctx.dialog_data.update(category=category)
        plan_id = dialog_manager.start_data['plan_id']
        quiz_type = dialog_manager.start_data['quiz_type']
        plan_tu = plans.find_one({'_id': ObjectId(plan_id)})
        quiz_params = {'q_ids': plan_tu['questions'], 'len': len(plan_tu['questions'])}
        ctx.dialog_data.update(selected_themes=plan_tu['themes'])
        ctx.dialog_data.update(quiz_params=quiz_params)
        ctx.dialog_data.update(quiz_type=quiz_type)
        ctx.dialog_data.update(plan_id=plan_id)
        selected_themes = ctx.dialog_data['selected_themes']
        len_themes = len(selected_themes)
    else:
        quiz_len = ctx.dialog_data['quiz_len']  # количество вопросов, которое захотел юзер
        s_themes = ctx.dialog_data['selected_themes']
        len_themes = len(s_themes)
        selected_themes = questions.distinct('theme') if len_themes == 0 else s_themes
        pipeline = [
            {'$match': {
                'theme': {'$in': selected_themes},
                'is_active': True,
                'multiple': False
            }},
            {'$sample': {'size': int(quiz_len)}},
            {'$group': {
                '_id': ObjectId(),
                'q_ids': {'$push': {"$toString": "$_id"}},
                'len': { '$sum': 1 }
            }},
        ]
        quiz_params = list(questions.aggregate(pipeline))[0]
        del quiz_params['_id']
        ctx.dialog_data.update(quiz_params=quiz_params)
    ctx.dialog_data.update(quiz_count=0)
    ctx.dialog_data.update(user_result={})  # данные о результате пользователя
    ctx.dialog_data['user_result']['count'] = 0
    ctx.dialog_data['user_result']['answers'] = []
    ctx.dialog_data['user_result']['answers_correct'] = []
    ctx.dialog_data['user_result']['errors_themes'] = []
    name_themes = (',\n'.join([themes.find_one({'code': code})['name'] for code in selected_themes])
                   if len_themes > 0
                   else 'Все темы из БД')
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
        articles_num = articles.count_documents({'theme': theme_code})
        have_articles = True if articles_num > 0 else False
        no_articles = not have_articles
    else:
        theme_name = ''
        errors_num = ''
        with_errors = False
        no_articles = False
        have_articles = False
    if context.dialog_data['category'] == 'tu_quiz':
        grade = context.dialog_data['grade']
        data = {
            'count': questions_count,
            'score': score,
            'errors_num': errors_num,
            'theme_name': theme_name,
            'with_errors': with_errors,
            'have_articles': have_articles,
            'no_articles': no_articles,
            'grade': grade,
            'button': 'Выход'
        }
    else:
        users_num = users.count_documents({})
        place = context.dialog_data.get('place', users_num)
        move_num = context.dialog_data.get('move_num', '0')
        move_sign = context.dialog_data.get('move_sign', '')
        move_sign = '📌' if move_num == '0' else move_sign
        move_num = '' if move_num == '0' else move_num
        data = {
            'count': questions_count,
            'score': score,
            'place': place,
            'users': users_num,
            'move_sign': move_sign,
            'move_num': move_num,
            'errors_num': errors_num,
            'theme_name': theme_name,
            'with_errors': with_errors,
            'have_articles': have_articles,
            'no_articles': no_articles,
            'button': 'Главное меню'
        }
    return data


async def get_quiz_report(dialog_manager: DialogManager, **middleware_data):
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


async def get_articles_data(dialog_manager: DialogManager, **middleware_data):
    context = dialog_manager.current_context()
    errors_themes = Counter(context.dialog_data['user_result']['errors_themes']).most_common(1)
    theme_code, _ = errors_themes[0]
    articles_qs = list(articles.find({'theme': theme_code}))
    articles_list = [(a['title'], a['link'], str(a['_id'])) for a in articles_qs]
    return {'articles': articles_list}


async def get_stats(dialog_manager: DialogManager, **middleware_data):
    user_id = dialog_manager.event.from_user.id
    user_data = results.find_one({'user_id': user_id})
    users_len = users.count_documents({})
    errors = user_data['errors_themes']
    has_errors = True if len(errors) > 0 else False
    if user_data is not None:
        data = {
            'quiz_count': user_data['quiz_count'],
            'questions_count': user_data['questions_count'],
            'score': user_data['score'],
            'place': user_data['place'],
            'users': users_len,
            'has_errors': has_errors,
        }
        return data


async def get_analysis_data(dialog_manager: DialogManager, **middleware_data):
    user_id = dialog_manager.event.from_user.id
    user_data = results.find_one({'user_id': user_id})
    errors = dict(sorted(user_data['errors_themes'].items(), key=lambda item: item[1], reverse=True))
    text = ''
    for code, errs in errors.items():
        theme_name = themes.find_one({'code': code})['name']
        text = f'{text}<b>{errs}</b> - {theme_name}\n'
    return {'text': text}
