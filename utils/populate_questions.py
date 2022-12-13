import pymongo

# from config.mongo_config import quiz

client = pymongo.MongoClient('localhost', 27017)
# Connect to our database
db = client['quiz_db']
quiz = db['questions']
# quiz_count = quiz.count_documents({})
# answer_num = quiz_count

file = 'quiz_raw.csv'
quiz_dict = {}
with open(file, 'r', encoding='UTF-8') as f:
    contents = f.readlines()
    for row in contents:
        question_dict = {}
        row_list = row.rstrip('\n').split(';')
        theme, question, correct_answer, num_answers, *answers = row_list
        question_dict['theme'] = theme
        question_dict['question'] = question
        question_dict['correct_answer'] = int(correct_answer)
        question_dict['num_answers'] = int(num_answers)
        question_dict['answers'] = answers
        quiz.insert_one(question_dict)
