# import datetime as dt
# import os

# from aiogram import Dispatcher, types
# from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters.state import State, StatesGroup
# from aiogram.utils.exceptions import CantInitiateConversation, BotBlocked

# from config.bot_config import bot, dp
# from config.mongo_config import attentions, offers, users
# from config.telegram_config import ADMIN_TELEGRAM_ID
# from texts.initial import SUB_TEXT
# from utils.constants import HELP_TEXT
# from utils.decorators import superuser_check


# router = Router()

# class BotOffer(StatesGroup):
#     waiting_for_offer = State()
#     waiting_for_offer_confirm = State()


# # обработка команды /users просмотр количества пользователей в БД
# @superuser_check
# async def count_users(message: types.Message):
#     queryset = users.distinct('full_name')
#     users_count = len(queryset)
#     final_text = '\n'.join(queryset)
#     await message.answer(
#         text=f'Количество пользователей в БД: {users_count}\n{final_text}'
#     )


# # обработка команды /offer - отзывы и предложения
# async def bot_offer(message: types.Message):
#     await message.answer(
#         text=(
#             f'Добрый день {message.from_user.full_name}.\n'
#             'Если у Вас есть предложения по улучшению работы бота - '
#             'напишите о них в следующем сообщении и мы сделаем всё '
#             'возможное для их осуществления.'
#             'Или нажмите /reset для отмены.'
#         ),
#     )
#     await BotOffer.waiting_for_offer.set()


# @dp.message_handler(state=BotOffer.waiting_for_offer)
# async def add_offer(message: types.Message, state: FSMContext):
#     await state.update_data(offer=message.text)
#     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     keyboard.add('Нет', 'Да')
#     await message.answer(
#         text='Вы точно хотите отправить отзыв о работе бота?',
#         reply_markup=keyboard,
#     )
#     await BotOffer.waiting_for_offer_confirm.set()


# @dp.message_handler(state=BotOffer.waiting_for_offer_confirm)
# async def confirm_offer(message: types.Message, state: FSMContext):
#     if message.text.lower() not in ['нет', 'да']:
#         await message.answer(
#             'Пожалуйста, отправьте "Да" или "Нет"'
#         )
#         return
#     if message.text.lower() == 'да':
#         buffer_data = await state.get_data()
#         offer = buffer_data['offer']
#         user = message.from_user
#         date = dt.datetime.today().strftime('%d.%m.%Y')
#         offers.insert_one(
#             {
#                 'date': date,
#                 'user_id': user.id,
#                 'offer': offer,
#             }
#         )
#         await message.answer(
#             text=('Отлично! Сообщение отправлено.\n'
#                   'Спасибо за отзыв!'),
#             reply_markup=types.ReplyKeyboardRemove()
#         )
#         await state.finish()
#         await bot.send_message(
#             chat_id=ADMIN_TELEGRAM_ID,
#             text=f'Получен новый отзыв от {user.full_name}:\n{offer}'
#         )
#     else:
#         await message.answer(
#             ('Хорошо. Отзыв не сохранен.\n'
#              'Если необходимо отправить новый отзыв - нажмите /offer'),
#             reply_markup=types.ReplyKeyboardRemove()
#         )
#         await state.reset_state()


# # обработка команды /log
# @superuser_check
# async def send_logs(message: types.Message):
#     file = 'logs_bot.log'
#     with open(file, 'rb') as f:
#         content = f.read()
#         await bot.delete_message(message.chat.id, message.message_id)
#         await bot.send_document(chat_id=ADMIN_TELEGRAM_ID, document=content)


# # @superuser_check
# async def upload_photo_attention(message: types.Message):
#     folder_path = os.path.join('./static', 'attention')
#     for year_dir in os.listdir(folder_path):
#         subfolder_path = os.path.join(folder_path, year_dir)
#         for filename in os.listdir(subfolder_path):
#             if filename.startswith('.'):
#                 continue
#             with open(os.path.join(subfolder_path, filename), 'rb') as photo:
#                 msg = await bot.send_photo(ADMIN_TELEGRAM_ID, photo, disable_notification=True)
#                 file_id = msg.photo[-1].file_id
#                 attentions.insert_one({'_id': file_id, 'year': int(year_dir)})


# async def help_handler(message: types.Message):
#     await message.answer(HELP_TEXT)


# async def subscribe_handler(message: types.Message):
#     all_users = list(users.find({}))
#     for user in all_users:
#         try:
#             await bot.send_message(
#                 chat_id=user.get('user_id'),
#                 text=SUB_TEXT
#             )
#         except (CantInitiateConversation, BotBlocked):
#             await bot.send_message(
#                 ADMIN_TELEGRAM_ID,
#                 f'Пользователь {user.get("full_name")} не доступен',
#             )


# def register_handlers_service(dp: Dispatcher):
#     dp.register_message_handler(count_users, commands='users')
#     dp.register_message_handler(send_logs, commands='log')
#     dp.register_message_handler(bot_offer, commands='offer')
#     dp.register_message_handler(upload_photo_attention, commands='upload_attention')
#     dp.register_message_handler(help_handler, commands='help')
#     dp.register_message_handler(subscribe_handler, commands='sub')
