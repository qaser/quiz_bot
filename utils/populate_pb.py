import json
import os

import pymongo

# from config.mongo_config import quiz

client = pymongo.MongoClient('localhost', 27017)
# Connect to our database
db = client['quiz_db']
questions = db['pb_questions']
answers = db['pb_answers']
link = db['pb_link']
instruction_sections = db['pb_instruction_sections']
nd_documents = db['pb_nd_documents']
nd = db['pb_nd']
program_groups = db['pb_program_groups']
acl = db['pb_acl']
answer_filter = db['pb_answer_filter']
designation = db['pb_designation']
divisions = db['pb_divisions']
nd_types = db['pb_nd_types']
programs = db['pb_programs']
rpo_program = db['pb_rpo_program']
rpo_isp_program = db['pb_rpo_isp_program']

db_camarada = client['camarada_db']
questions_test = db_camarada['questions']
answers_test = db_camarada['answers']
docs = db_camarada['docs']

docs_id = {
    13: 'fz_116',
    22: 'rpo_vysota',
    28: 'sto_eb',
    30: 'sto_eb',
    35: 'bdd',
    39: 'risk_theory',
    41: 'bdd',
    45: 'rpo_or',
    46: 'sto_pemg',
    49: 'gas_theory',
    48: 'gas_theory',
    52: 'risk_theory',
    72: 'rpo_zem',
    74: 'rpo_gruz',
    459: 'rpo_or',
    75: 'ot_tu',
    76: 'rpo_or',
    77: 'rpo_gor',
}

not_random_phrase = [
    'перечисленные выше',
    'перечисленые выше',
    'ответы верны',
    'указаны в отв',
    'перечисленное выше',
    'перечисленое выше',
    'указанное в отв',
    'указаное в отв',
    'перечисленные в отв',
    'перечисленые в отв',
    'указанное в отв',
    'указаное в отв',
    'в ответе',
    'в ответах',
    'указанное выше',
    'указанные выше',
    'верные ответы',
    'все перечисленные',
    'перечисленных выше',
    'перечисленых выше',
    'совместно',
    'ответы',
    'ответ',
    'указаное выше',
    'указаные выше',
]


def populate_testing_questions():
    for id, theme_code in docs_id.items():
        sections = list(instruction_sections.find({'id_instructions': id}))
        sections_ids = [sec['p_id'] for sec in sections]
        queryset = list(questions.find({'id_instruction_sections': {'$in': sections_ids}, 'deleted': 0}))
        doc = nd_documents.find_one({'p_id': id})
        new_doc = docs.insert_one(
            {
                'name': doc['document_name'],
                'description': doc['description'],
                'is_active': True,
                'theme': theme_code,
            }
        )
        for q in queryset:  # вставка вопросов
            qt = questions_test.insert_one(
                {
                    'theme': theme_code,
                    'text': q['text'],
                    'multiple': True if q['multiple'] == 1 else False,
                    'is_active': True,
                    'doc': new_doc.inserted_id,
                }
            )
            answers_qs = list(answers.find({'id_questions': q['p_id'], 'deleted': 0}))
            if len(answers_qs) < 7:
                for ans in answers_qs:  # вставка ответов
                    ans_text = ans['answer']
                    for phrase in not_random_phrase:
                        if ans_text.lower().find(phrase) != -1:
                            questions_test.update_one(
                                {'_id': qt.inserted_id},
                                {'$set': {'random_allows': False}},
                            )
                    answers_test.insert_one(
                        {
                            'q_id': qt.inserted_id,
                            'is_active': True,
                            'text': ans['answer'],
                            'is_correct': True if ans['correct_answer'] == 1 else False,
                        }
                    )
                is_random_allowed = questions_test.find_one({'_id': qt.inserted_id}).get('random_allows', None)
                if is_random_allowed is None:
                    questions_test.update_one(
                        {'_id': qt.inserted_id},
                        {'$set': {'random_allows': True}},
                    )


populate_testing_questions()


# script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
# rel_path = "../db"
# cur_path = os.path.join(script_dir, rel_path)


# for filename in os.listdir(cur_path):
#     # if filename == 'answers.json' or filename == 'questions.json':
#     with open(os.path.join(cur_path, filename), 'r', encoding="utf-8") as f:
#         print(filename)
#         name, _ = filename.split('.')
#         coll_name = f'pb_{name}'
#         data = json.load(f)
#         db[coll_name].insert_many(data)


# отдельная выборка по РПО
# program_id = programs.find_one({'id_program_groups': 100000227}).get('p_id')
# links = list(link.find({'id_programs': program_id}))
# res = [lk['id_nd_documents'] for lk in links]
# print(set(res))
# for id in set(res):
#     doc = nd_documents.find_one({'p_id': id})['document_name']
#     print(id, doc)
# for lk in links:
#     pb_questions = list(questions.find({'id_instruction_sections': lk.get('id_instruction_sections')}))
#     res = res + pb_questions
# for id, q in enumerate(res):
#     rpo_program.insert_one({'count': (id + 1), 'id_question': q.get('p_id')})


# # отдельная выборка по РПО ИСП
# program_id = programs.find_one({'id_program_groups': 100000230}).get('p_id')
# links = list(link.find({'id_programs': program_id}))
# res = []
# for lk in links:
#     pb_questions = list(questions.find({'id_instruction_sections': lk.get('id_instruction_sections')}))
#     res = res + pb_questions
# for id, q in enumerate(res):
#     rpo_isp_program.insert_one({'count': (id + 1), 'id_question': q.get('p_id')})
