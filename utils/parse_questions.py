import docx
import pymongo

client = pymongo.MongoClient('localhost', 27017)
db = client['quiz_db']
answers = db['pb_answers']
questions = db['pb_questions']
program = db['pb_rpo_program']

doc = docx.Document('questions.docx')

data = []
count = 0

for para in doc.paragraphs:
    text = para.text
    if text.startswith(' ') is False:
        q_search = list(questions.find(
            {'$text': {'$search': f'\"{text}\"'}}
        ))
        if len(q_search) == 1:
            count = count + 1
            q_id = int(q_search[0].get('p_id'))
            program.insert_one({'count': count, 'id_question': q_id})
    # if text[0] == ' ':
#         data.append(text)
# print(data)

# for id, row in enumerate(table.rows):
#     works.insert_one(
#         {
#             'num': id+1,
#             'type': row.cells[1].text,
#             'department': row.cells[2].text,
#             'sub_department': row.cells[3].text,
#             'text': row.cells[4].text,
#             'date': row.cells[5].text,
#         }
#     )
