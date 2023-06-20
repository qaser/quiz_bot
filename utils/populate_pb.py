import pymongo
import os
import json

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
# quiz_count = quiz.count_documents({})
# answer_num = quiz_count

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
rel_path = "../db"
cur_path = os.path.join(script_dir, rel_path)


for filename in os.listdir(cur_path):
    if filename == 'answers.json' or filename == 'questions.json':
        with open(os.path.join(cur_path, filename), 'r', encoding="utf-8") as f:
            print(filename)
            name, _ = filename.split('.')
            coll_name = f'pb_{name}'
            data = json.load(f)
            db[coll_name].insert_many(data)


# отдельная выборка по РПО
program_id = programs.find_one({'id_program_groups': 100000227}).get('p_id')
links = list(link.find({'id_programs': program_id}))
res = []
for lk in links:
    pb_questions = list(questions.find({'id_instruction_sections': lk.get('id_instruction_sections')}))
    res = res + pb_questions
for id, q in enumerate(res):
    rpo_program.insert_one({'count': (id + 1), 'id_question': q.get('p_id')})


# отдельная выборка по РПО ИСП
program_id = programs.find_one({'id_program_groups': 100000230}).get('p_id')
links = list(link.find({'id_programs': program_id}))
res = []
for lk in links:
    pb_questions = list(questions.find({'id_instruction_sections': lk.get('id_instruction_sections')}))
    res = res + pb_questions
for id, q in enumerate(res):
    rpo_isp_program.insert_one({'count': (id + 1), 'id_question': q.get('p_id')})
