db.users.updateOne({'full_name': 'Сергей'},{'$set': {'full_name': 'Иванов С.Н.'}})
db.results.findOne({'user_id': 1747036217})
db.results.updateOne({'user_id': 1747036217},{$set: {'done': 'false'}})

db.users.findOne({'full_name': 'Егор'})
