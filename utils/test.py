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
buffer = db['buffer']


THEMES = {
    'apk': 'АПК',
    'bptpg': 'БПТПГ',
    'first_aid': 'Первая помощь',
    'gor': 'Газоопасные работы',
    'gpa-с-16': 'Агрегат ГПА-Ц-16',
    'gtd': 'Теория ГТУ (ГТД)',
    'gtk-25i': 'Агрегат ГТК-25И',
    'kip': 'КИПиА',
    'ks': 'КС (общая тема)',
    'ms': 'Маслосистема КЦ',
    'ms_nc-16-76': 'Маслосистема НЦ-16/76',
    'ms_nk-16st': 'Маслосистема НК-16СТ',
    'nc-16-76': 'Нагнетатель НЦ-16/76',
    'nk-16st': 'ГТД НК-16СТ',
    'or': 'Огневые работы',
    'ot': 'Охрана труда',
    'pb': 'Промышленная безопасность',
    'pemg': 'ПЭМГ',
    'pump': 'Нагнетатель (теория)',
    'srd': 'СРД',
    'tpa': 'ТПА',
    'vysota': 'Работы на высоте',
    'zem': 'Земляные работы',
}

for code, name in THEMES.items():
    themes.insert_one({'code': code, 'name': name})
