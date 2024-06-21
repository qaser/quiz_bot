from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode

from dialogs.for_tu import windows
from dialogs.for_tu.states import Tu

router = Router()
dialog =  Dialog(
    windows.main_menu_window(),
    windows.select_year_window(),
    windows.select_quarter_window(),
    windows.select_themes_window(),
    windows.select_date_window(),
    windows.save_plan_window(),
    # windows.export_test(),
    # windows.plan_review_window(),
)


@router.message(Command('tu'))
async def blpu_request(message: Message, dialog_manager: DialogManager):
    await message.delete()
    # Important: always set `mode=StartMode.RESET_STACK` you don't want to stack dialogs
    await dialog_manager.start(Tu.select_category, mode=StartMode.RESET_STACK)



# import datetime as dt
# import os

# from aiogram import Dispatcher, types
# from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters import Text
# from aiogram.dispatcher.filters.state import State, StatesGroup

# from config.bot_config import bot, dp
# from config.mongo_config import plans, questions, themes, users
# from utils.constants import DEPARTMENTS
# from utils.decorators import admin_check
# from utils.save_docx_file import create_docx_file


# router = Router()

# NUM_QUESTIONS = 30


# class Plan(StatesGroup):
#     waiting_department = State()
#     waiting_year = State()
#     waiting_quarter = State()
#     waiting_themes = State()
#     waiting_confirm = State()


# # создание списка тем на квартал (шаблон)
# @admin_check
# async def create_plan(message: types.Message):
#     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     for dep in DEPARTMENTS:
#         keyboard.add(dep)
#     await message.answer('Выберите службу', reply_markup=keyboard)
#     await Plan.waiting_department.set()


# @dp.message_handler(state=Plan.waiting_department)
# async def choose_year(message: types.Message, state: FSMContext):
#     if message.text not in DEPARTMENTS:
#         await message.answer(
#             'Пожалуйста, выберите службу, используя список ниже.'
#         )
#         return
#     await state.update_data(department=message.text)
#     now_year = dt.datetime.now().year
#     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     keyboard.add(str(now_year), str(now_year + 1))
#     await message.answer('Выберите год планирования', reply_markup=keyboard)
#     await Plan.waiting_year.set()


# @dp.message_handler(state=Plan.waiting_year)
# async def choose_quarter(message: types.Message, state: FSMContext):
#     now_year = dt.datetime.now().year
#     if message.text not in [str(now_year), str(now_year + 1)]:
#         await message.answer('Пожалуйста, выберите год, используя список ниже.')
#         return
#     await state.update_data(year=message.text)
#     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     keyboard.add('1', '2')
#     keyboard.add('3', '4')
#     await message.answer('Выберите квартал планирования', reply_markup=keyboard)
#     await Plan.waiting_quarter.set()


# @dp.message_handler(state=Plan.waiting_quarter)
# async def choose_themes(message: types.Message, state: FSMContext):
#     # TODO сделать проверку на наличие плана на эти даты
#     if message.text not in ['1', '2', '3', '4']:
#         await message.answer('Пожалуйста, выберите квартал, используя список ниже.')
#         return
#     await state.update_data(quarter=message.text)
#     await state.update_data(themes=[])
#     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     keyboard.add('<< Завершить выбор >>')
#     themes_queryset = themes.distinct('name')
#     for theme in themes_queryset:
#         keyboard.add(theme)
#     await message.answer(
#         text=(
#             'Выберите темы занятий (не более десяти).\n'
#             'При необходимости нажмите "Завершить выбор"'
#         ),
#         reply_markup=keyboard,
#     )
#     await Plan.waiting_themes.set()


# @dp.message_handler(state=Plan.waiting_themes)
# async def create_list_themes(message: types.Message, state: FSMContext):
#     themes_queryset = themes.distinct('name')
#     if message.text.lower() != '<< завершить выбор >>':
#         if message.text not in themes_queryset:
#             await message.answer('Пожалуйста, выберите тему, используя список ниже.')
#             return
#         for value in themes_queryset:
#             if value == message.text:
#                 theme = themes.find_one({'name': value}).get('code')
#         data = await state.get_data()
#         list_themes = data['themes']
#         if theme not in list_themes:
#             list_themes.append(theme)
#         await state.update_data(themes=list_themes)
#         await message.answer('Если необходимо выберите ещё тему')
#         return
#     else:
#         keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#         keyboard.add('Нет', 'Да')
#         data = await state.get_data()
#         dep, year = data['department'], data['year']
#         quarter = data['quarter']
#         thms = data['themes']
#         if len(thms) == 0:
#             await message.answer('Необходимо выбрать минимум одну тему')
#             return
#         text_themes = ''
#         for i in thms:
#             name = themes.find_one({'code': i}).get('name')
#             text_themes = '{}\n    {}'.format(text_themes, name)
#         await message.answer(
#             text=(
#                 'Вы выбрали:\n'
#                 f'Служба - {dep}\n'
#                 f'Период планирования - {quarter} кв. {year} г.\n'
#                 f'Темы занятий:\n{text_themes}'
#                 '\n\nСохранить?'
#             ),
#             reply_markup=keyboard,
#         )
#         await Plan.waiting_confirm.set()


# @dp.message_handler(state=Plan.waiting_confirm)
# async def plan_save(message: types.Message, state: FSMContext):
#     # TODO сделать ограничение на количество тем (10)
#     if message.text.lower() not in ['нет', 'да']:
#         await message.answer('Пожалуйста, отправьте "Да" или "Нет"')
#         return
#     if message.text.lower() == 'да':
#         pipeline = [{'$match': {'theme': theme}}, {'$sample': {'size': num_q}}]
#         data = await state.get_data()
#         dep, year = data['department'], int(data['year'])
#         quarter = int(data['quarter'])
#         themes = data['themes']
#         user_id = message.from_user.id
#         q_list = []
#         num_themes = len(themes)
#         num_q = NUM_QUESTIONS // num_themes
#         for theme in themes:
#             list_questions = list(questions.aggregate(pipeline))
#             q_ids = [q.get('_id') for q in list_questions]
#             q_list = q_list + q_ids
#         plan_check = plans.find_one(
#             {'year': year, 'quarter': quarter, 'department': dep}
#         )
#         if plan_check is not None:
#             plans.update_one(
#                 {'year': year, 'quarter': quarter, 'department': dep},
#                 {'$set': {'owner': user_id, 'themes': themes, 'questions': q_list}}
#             )
#         else:
#             plans.insert_one(
#                 {
#                     'year': year,
#                     'quarter': quarter,
#                     'department': dep,
#                     'owner': user_id,
#                     'themes': themes,
#                     'questions': q_list
#                 }
#             )
#         await message.answer(
#             'Запись успешно добавлена. Тесты сформированы',
#             reply_markup=types.ReplyKeyboardRemove()
#         )
#         await state.finish()
#     else:
#         await message.answer(
#             'Данные не сохранены',
#             reply_markup=types.ReplyKeyboardRemove()
#         )
#         await state.reset_state()


# @admin_check
# async def show_themes(message: types.Message):
#     text = ''
#     queryset = list(questions.find({}))
#     count_q = len(queryset)
#     for theme in list(themes.find()):
#         name = theme['name']
#         code = theme['code']
#         res = len(list(questions.find({'theme': code})))
#         if res != 0:
#             text = f'{text}\n{name}: {res}'
#     await message.answer(f'Количество вопросов в БД:\n{text}\n\nВсего: {count_q}')


# # экспорт вопросов в файл
# @admin_check
# async def export_tests(message: types.Message):
#     keyboard = types.InlineKeyboardMarkup(row_width=3)
#     user_id = message.from_user.id
#     department = users.find_one({'user_id': user_id}).get('department')
#     years = plans.find({'department': department}).distinct('year')
#     buttons = [types.InlineKeyboardButton(
#         text=str(year),
#         callback_data=f'plan_{year}_{user_id}_{department}'
#     ) for year in years]
#     keyboard.add(*buttons)
#     await message.delete()
#     await message.answer(
#         'Функция экспорта тестовых вопросов в файл. Выберите год',
#         reply_markup=keyboard
#     )


# @dp.callback_query_handler(Text(startswith='plan_'))
# async def get_test_quarter(call: types.CallbackQuery):
#     _, year, user_id, department = call.data.split('_')
#     quarters = plans.find({'department': department, 'year': int(year)}).distinct('quarter')
#     keyboard = types.InlineKeyboardMarkup(row_width=4)
#     buttons = [
#         types.InlineKeyboardButton(
#             text=str(quarter),
#             callback_data=f'pln_{year}_{quarter}_{user_id}_{department}'
#         ) for quarter in quarters
#     ]
#     await call.message.delete_reply_markup()
#     keyboard.add(*buttons)
#     await call.message.edit_text('Выберите квартал:', reply_markup=keyboard)


# @dp.callback_query_handler(Text(startswith='pln_'))
# async def get_test_document(call: types.CallbackQuery):
#     _, year, quarter, user_id, department = call.data.split('_')
#     plan = plans.find_one(
#         {
#             'department': department,
#             'year': int(year),
#             'quarter': int(quarter)
#         }
#     )
#     await call.message.delete_reply_markup()
#     await call.message.edit_text('Запрос получен')
#     create_docx_file(plan)
#     path = f'static/reports/Тест {department} ({quarter} кв. {year}г).docx'
#     await bot.send_document(chat_id=user_id, document=open(path, 'rb'))
#     os.remove(path)
#     await call.message.delete()


# def register_handlers_plan(dp: Dispatcher):
#     dp.register_message_handler(create_plan, commands='plan')
#     dp.register_message_handler(show_themes, commands='themes')
#     dp.register_message_handler(export_tests, commands='export_tests')
