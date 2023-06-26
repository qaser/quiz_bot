import pymongo
import os
import json

# from config.mongo_config import quiz

client = pymongo.MongoClient('localhost', 27017)
# Connect to our database
db = client['quiz_db']
rpo_program = db['pb_rpo_program']

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
rel_path = "../db"
cur_path = os.path.join(script_dir, rel_path)



with open(os.path.join(cur_path, 'quiz_db.pb_rpo_program.json'), 'r', encoding="utf-8") as f:
    data = json.load(f)
    rpo_program.insert_many(data)
