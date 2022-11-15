# import random

# from aiogram import Dispatcher, types

# from config.bot_config import bot
# from config.mongo_config import quiz



# def get_poll():
#     count = quiz.count_documents({})
#     rand_num = random.randint(0, count)
#     poll = quiz.find_one({'num': rand_num})
#     return poll


# async def send_quiz_shedule():
#     poll = get_poll()
#     correct_option_id = poll['correct_answer'] - 1
#     explanation = poll['answers'][poll['correct_answer'] - 1]
#     await bot.send_poll(
#         chat_id=CHAT_ID,
#         question=poll['question'],
#         options=poll['answers'],
#         is_anonymous=True,
#         type='quiz',
#         correct_option_id=correct_option_id,
#         explanation=f'Правильный ответ: {explanation}',
#         protect_content=True,
#     )


# async def send_quiz(message: types.Message):
#     poll = get_poll()
#     correct_option_id = poll['correct_answer'] - 1
#     explanation = poll['answers'][poll['correct_answer'] - 1]
#     await bot.send_poll(
#         chat_id=message.chat.id,
#         question=poll['question'],
#         options=poll['answers'],
#         is_anonymous=True,
#         type='quiz',
#         correct_option_id=correct_option_id,
#         explanation=f'Правильный ответ: {explanation}',
#         protect_content=True,
#     )
#     await bot.send_message(message.chat.id, text=QUIZ_TEXT)


# def register_handlers_quiz(dp: Dispatcher):
#     dp.register_message_handler(send_quiz, commands='vopros')
