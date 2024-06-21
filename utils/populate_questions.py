import re

import pymongo

client = pymongo.MongoClient('localhost', 27017)
db = client['camarada_db']
questions = db['questions']
themes = db['themes']
answers = db['answers']


def check_solid_questions():  # функция проверки наличия правильного ответа или нескольких правильных ответов
    qs = list(questions.find({}))
    for q in qs:
        q_id = q['_id']
        ans_count = answers.count_documents({'q_id': q_id, 'is_correct': True})
        if ans_count == 0 or ans_count > 1:
            print(q_id)
            # answers.delete_many({'q_id': q_id})
            # questions.delete_one({'_id': q_id})


def find_questions_tail():  # функция для поиска указания пунктов в тексте вопроса
    qs = list(questions.find({}))
    for q in qs:
        text = q['text']
        pattern = re.compile('\(.+\)')
        result = pattern.findall(rf'{text}')
        if len(result) == 1:
            print(result[0])
            # unit = result[0]
            # new_text = text.replace(unit, '')
            # questions.update_one({'_id': q['_id']}, {'$set': {'text': new_text}})


def populate_questions_and_answers():
    file = 'fixtures/quiz_raw.csv'
    with open(file, 'r', encoding='UTF-8') as f:
        contents = f.readlines()
        for row in contents:
            question_dict = {}
            row_list = row.rstrip('\n').split(';')
            theme, text, correct_answer, num_answers, *answs = row_list
            question_dict['theme'] = theme
            question_dict['text'] = text
            question_dict['doc'] = None  # нужно потом скорректировать
            question_dict['multiple'] = False
            question_dict['is_active'] = True
            question_dict['random_allows'] = True
            q_id = questions.insert_one(question_dict).inserted_id
            for i, ans in enumerate(answs[:int(num_answers)]):
                answer_dict = {}
                answer_dict['q_id'] = q_id
                answer_dict['is_active'] = True
                answer_dict['text'] = ans
                answer_dict['is_correct'] = True if ((i + 1) == int(correct_answer)) else False
                answers.insert_one(answer_dict)



def populate_themes():
    file = 'fixtures/themes.csv'
    with open(file, 'r', encoding='UTF-8') as f:
        contents = f.readlines()
        for row in contents:
            row_list = row.rstrip('\n').split(';')
            code, name = row_list
            themes.update_one(
                {'code': code},
                {'$set': {'name': name}},
                upsert=True
            )
