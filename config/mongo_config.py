import pymongo

# Create the client
client = pymongo.MongoClient('localhost', 27017)
db = client['knowledge_db']
quiz = db['quiz']
users = db['users']
offers = db['offers']
results = db['results']


''' 
структура данных results
    '_id': дефолтный первичный ключ
    'user': id пользователя телеграм
    'year': год проверки знаний
    'quarter': квартал года
    'test_type': тип теста (входной или выходной)
    'done': прошел проверку знаний (булево)
    'quiz': список из кортежей (id вопроса, id ответа, ответ дан правильно\неправильно)
    'result': оценка за тест

структура данных пользователя
    '_id': дефолтный первичный ключ
    'user_id': id пользователя телеграм
    'first_name': имя пользователя,
    'last_name': фамилия пользователя,
    'full_name': имя и фамилия пользователя
    'username':  логин пользователя
    'department': место работы (опционально)

структура данных вопросов
    '_id': дефолтный первичный ключ
    'num': номер вопроса
    'theme' тематика вопроса
    'question' вопрос (не более 200 знаков)
    'correct_answer' индекс правильного ответа
    'num_answers' количество ответов (не более 10-ти)
    'answers' ответы (список)

структура данных администраторов
    '_id': дефолтный первичный ключ
    'user_id' id пользователя телеграм
    'username': имя пользователя

структура данных шаблонов теста
    '_id': дефолтный первичный ключ
    'year': год проверки знаний
    'quarter': квартал года
    'themes': темы вопросов квартала (список)
'''