import pymongo
from aiogram.contrib.fsm_storage.mongo import MongoStorage

# Create the client
client = pymongo.MongoClient('localhost', 27017)
storage = MongoStorage(host='localhost', port=27017, db_name='aiogram_fsm')
db = client['quiz_db']
themes = db['themes']
users = db['users']
admin_requests = db['admin_requests']
offers = db['offers']
results = db['results']
questions = db['questions']
plans = db['plans']
terms = db['terms']
key_rules = db['key_rules']
attentions = db['attentions']
plan_tu = db['plan_tu']
buffer = db['buffer']
# коллекции для тестов РПО
pb_questions = db['pb_questions']
pb_answers = db['pb_answers']
pb_link = db['pb_link']
pb_instruction_sections = db['pb_instruction_sections']
pb_nd_documents = db['pb_nd_documents']
pb_nd = db['pb_nd']
pb_program_groups = db['pb_program_groups']
pb_users_stats = db['pb_users_stats']
pb_programs = db['pb_programs']
# отдельная выборка по РПО
pb_rpo_program = db['pb_rpo_program']
pb_rpo_isp_program = db['pb_rpo_isp_program']




'''
структура данных results
    '_id': дефолтный первичный ключ
    'user_id': id пользователя телеграм
    'year': год проверки знаний
    'quarter': квартал года
    'test_type': тип теста (входной или выходной)
    'done': прошел проверку знаний (булево)
    'quiz_results': список из кортежей
    'grade': оценка за тест

структура данных users
    '_id': дефолтный первичный ключ
    'user_id': id пользователя телеграм
    'first_name': имя пользователя,
    'last_name': фамилия пользователя,
    'full_name': имя и фамилия пользователя
    'username':  логин пользователя
    'department': место работы (опционально)
    'is_admin': по умолчанию false

структура данных question
    '_id': дефолтный первичный ключ
    'theme' тематика вопроса
    'question' вопрос (не более 200 знаков)
    'correct_answer' индекс правильного ответа
    'answers' ответы (список)

структура данных планов (plans)
    '_id': дефолтный первичный ключ
    'department': наименование службы
    'year': год проверки знаний
    'quarter': квартал года
    'themes': темы вопросов квартала (список)
    'owner': кто составил
    'questions' id вопросов список

структура данных admin_requests
    '_id' дефолтный первичный ключ
    'user_id' id юзера
    'username' имя пользователя
    'comment' комментарий

структура данных themes
    '_id' дефолтный первичный ключ
    'code' id юзера
    'name' имя пользователя

структура данных definitions
    '_id' дефолтный первичный ключ
    'theme_code': код темы
    'theme': тематика терминов
    'name': название термина
    'description': описание термина

структура данных plan_tu
    'department' наименование подразделения
    'plan': словарь с даными вида: {'date': дата, 'theme: название темы, 'doc':ссылка на документ}


'''
