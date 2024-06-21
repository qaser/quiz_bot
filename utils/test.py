import datetime as dt

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
conditions = db['conditions']
admin_requests = db['admin_requests']
plans = db['plans']
results_tu = db['results_tu']
scheduler_tu = db['scheduler']


users.update_many({}, {'$set': {"conditions_agree": False}})
