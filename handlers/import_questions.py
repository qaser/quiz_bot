# import os

# import openpyxl
# from aiogram import Dispatcher, types
# from openpyxl.utils import get_column_letter

# from config.bot_config import bot, dp
# from config.mongo_config import questions, themes
# from utils.utils import word_conjugate

# # TODO сделать импорт тем из excel файла


# router = Router()

# async def import_file(message: types.Message):
#     await message.answer('Отправьте следующим сообщением файл с вопросами')


# @dp.message_handler(content_types=types.ContentType.DOCUMENT)
# async def download_file(message):
#     file_name = message.document.file_name
#     if file_name.endswith('.xlsx'):
#         file_id = message.document.file_id
#         file = await bot.get_file(file_id)
#         file_path = file.file_path
#         await bot.download_file(
#             file_path=file_path,
#             destination=r'static/questions.xlsx'
#         )
#         await import_from_excel(message.from_user.id)
#     else:
#         await bot.answer(
#             'Данный тип файлов не поддерживается.\n'
#             'Скачайте шаблон введя команду /example'
#         )


# async def import_from_excel(user_id):
#     wbook = openpyxl.load_workbook('static/questions.xlsx')
#     sheet_q = wbook['questions']
#     sheet_t = wbook['themes']
#     num_rows_q = sheet_q.max_row
#     num_rows_t = sheet_t.max_row
#     count_q = 0
#     for row in range(2, (num_rows_q + 1)):
#         num_ans = sheet_q['D' + str(row)].value
#         theme = sheet_q['A' + str(row)].value
#         answers = []
#         for num in range(5, (num_ans + 5)):
#             ans = str(sheet_q[get_column_letter(num) + str(row)].value)
#             if ans == '' or ans is None or ans == 'null' or len(ans) > 100:
#                 break
#             answers.append(ans)
#         if len(answers) < num_ans:
#             continue
#         if theme is not None:
#             questions.insert_one({
#                 'theme': theme,
#                 'question': sheet_q['B' + str(row)].value,
#                 'correct_answer': sheet_q['C' + str(row)].value,
#                 'num_answers': num_ans,
#                 'answers': answers,
#             })
#             count_q += 1
#     for row in range(2, (num_rows_t + 1)):
#         name = sheet_t['B' + str(row)].value
#         code = sheet_t['A' + str(row)].value
#         if name is not None and code is not None:
#             themes.update_one(
#                 {'code': code},
#                 {'$set': {'name': name}},
#                 upsert=True
#             )
#     os.remove('static/questions.xlsx')
#     words_q = ['вопрос', 'вопроса', 'вопросов']
#     words_z = ['Загружен', 'Загружено', 'Загружено']
#     text_q = word_conjugate(count_q, words_q)
#     text_z = word_conjugate(count_q, words_z)
#     await bot.send_message(
#         chat_id=user_id,
#         text=f'Файл получен.\n{text_z} {count_q} {text_q} из {num_rows_q-1}.'
#     )


# async def send_example(message: types.Message):
#     await message.answer_document(open('static/example/questions.xlsx', 'rb'))


# def register_handlers_excel(dp: Dispatcher):
#     dp.register_message_handler(import_file, commands='import')
#     dp.register_message_handler(send_example, commands='example')
