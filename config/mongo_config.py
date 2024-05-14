import pymongo

# Create the client
client = pymongo.MongoClient('localhost', 27017)

db = client['quiz_db']
themes = db['themes']
users = db['users']
terms = db['terms']
questions = db['questions']
answers = db['answers']
results = db['results']
articles = db['articles']
docs = db['docs']

buffer = db['buffer']
results_ks = db['results_ks']
admin_requests = db['admin_requests']
offers = db['offers']
plans = db['plans']
key_rules = db['key_rules']
plan_tu = db['plan_tu']
videos = db['videos']


'''
структура данных users
    '_id': дефолтный первичный ключ
    'user_id': id пользователя телеграм
    'first_name': имя пользователя,
    'last_name': фамилия пользователя,
    'full_name': имя и фамилия пользователя
    'username':  логин пользователя
    'is_admin': по умолчанию false
    'department': место работы (опционально)

структура данных questions
    '_id': дефолтный первичный ключ
    'theme' тематика вопроса
    'text' вопрос
    'doc' документ, id документа
    'multiple' несколько ответов
    'random_allows' можно перемешать ответы
    'is_active' активный вопрос

структура данных answers
    '_id':
    'q_id': id вопроса
    'is_correct': True/False
    'is_active': True/False
    'text': текст ответа

структура данных terms
    '_id' дефолтный первичный ключ
    'theme_code': код темы
    'name': название термина
    'description': описание термина

структура данных results
    '_id': дефолтный первичный ключ
    'user_id': id пользователя телеграм
    'score': количество набранных очков (всего)
    'questions_count': количество пройденных вопросов
    'quiz_count': количество пройденных тестов
    'errors_themes': {theme_code: errors_count'}

структура данных articles
    '_id': дефолтный первичный ключ
    'user_id': id пользователя телеграм, добавившего статью
    'theme': код темы
    'tags': список тегов
    'title': название статьи
    'date': дата добавления в БД
    'link': ссылка

структура данных results_ks
    '_id': дефолтный первичный ключ
    'user_id': id пользователя телеграм
    'year': год проверки знаний
    'quarter': квартал года
    'test_type': тип теста (входной или выходной)
    'done': прошел проверку знаний (булево)
    'quiz_results': список из кортежей
    'grade': оценка за тест

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
