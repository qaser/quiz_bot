import datetime as dt

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from config.mongo_config import plans
from config.bot_config import dp
from scheduler.scheduler_func import add_questions_in_plan
from utils.constants import DEPARTMENTS, THEMES
from utils.decorators import admin_check


class Plan(StatesGroup):
    waiting_department = State()
    waiting_year = State()
    waiting_quarter = State()
    waiting_themes = State()
    waiting_confirm = State()


# создание списка тем на квартал (шаблон)
@admin_check
async def create_plan(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for dep in DEPARTMENTS:
        keyboard.add(dep)
    await message.answer(
        text='Выберите службу',
        reply_markup=keyboard,
    )
    await Plan.waiting_department.set()


@dp.message_handler(state=Plan.waiting_department)
async def choose_year(message: types.Message, state: FSMContext):
    if message.text not in DEPARTMENTS:
        await message.answer(
            'Пожалуйста, выберите службу, используя список ниже.'
        )
        return
    await state.update_data(department=message.text)
    now_year = dt.datetime.now().year
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(str(now_year), str(now_year + 1))
    await message.answer(
        text='Выберите год планирования',
        reply_markup=keyboard,
    )
    await Plan.waiting_year.set()


async def choose_quarter(message: types.Message, state: FSMContext):
    now_year = dt.datetime.now().year
    if message.text not in [str(now_year), str(now_year + 1)]:
        await message.answer(
            'Пожалуйста, выберите год, используя список ниже.'
        )
        return
    await state.update_data(year=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('1', '2')
    keyboard.add('3', '4')
    await message.answer(
        text='Выберите квартал планирования',
        reply_markup=keyboard,
    )
    await Plan.waiting_quarter.set()


async def choose_themes(message: types.Message, state: FSMContext):
    # TODO сделать проверку на наличие плана на эти даты
    if message.text not in ['1', '2', '3', '4']:
        await message.answer(
            'Пожалуйста, выберите квартал, используя список ниже.'
        )
        return
    await state.update_data(quarter=message.text)
    await state.update_data(themes=[])
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('<< Завершить выбор >>')
    for theme in THEMES.values():
        keyboard.add(theme)
    await message.answer(
        text=(
            'Выберите темы занятий (не более десяти).\n'
            'При необходимости нажмите "Завершить выбор"'
        ),
        reply_markup=keyboard,
    )
    await Plan.waiting_themes.set()


async def create_list_themes(message: types.Message, state: FSMContext):
    # TODO сделать проверку на повторный ввод одинаковых тем
    if message.text.lower() != '<< завершить выбор >>':
        if message.text not in THEMES.values():
            await message.answer(
                'Пожалуйста, выберите тему, используя список ниже.'
            )
            return
        for key, value in THEMES.items():
            if value == message.text:
                theme = key
        data = await state.get_data()
        list_themes = data['themes']
        list_themes.append(theme)
        await state.update_data(themes=list_themes)
        await message.answer('Если необходимо выберите ещё тему')
        return
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Нет', 'Да')
        data = await state.get_data()
        dep, year = data['department'], data['year']
        quarter, themes = data['quarter'], data['themes']
        text_themes = ''
        for i in themes:
            name = THEMES.get(i)
            text_themes = '{}\n{}'.format(text_themes, name)
        await message.answer(
            text=(
                'Вы выбрали:\n'
                f'Служба - {dep}\n'
                f'Период планирования - {quarter} кв. {year} г.\n'
                f'Темы занятий:{text_themes}'
                '\nСохранить?'
            ),
            reply_markup=keyboard,
        )
        await Plan.waiting_confirm.set()


async def plan_save(message: types.Message, state: FSMContext):
    # TODO сделать проверку на пустой список тем
    # TODO сделать ограничение на количество тем (10)
    if message.text.lower() not in ['нет', 'да']:
        await message.answer(
            'Пожалуйста, отправьте "Да" или "Нет"'
        )
        return
    if message.text.lower() == 'да':
        data = await state.get_data()
        dep, year = data['department'], int(data['year'])
        quarter, themes = int(data['quarter']), data['themes']
        user_id = message.from_user.id
        plan_check = plans.find_one(
            {'year': year, 'quarter': quarter, 'department': dep}
        )
        if plan_check is not None:
            plans.update_one(
                {'year': year, 'quarter': quarter, 'department': dep},
                {'$set': {'owner': user_id, 'themes': themes}}
            )
        else:
            plans.insert_one(
                {
                    'year': year,
                    'quarter': quarter,
                    'department': dep,
                    'owner': user_id,
                    'themes': themes

                }
            )
        await message.answer(
            'Запись успешно добавлена',
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.finish()
    else:
        await message.answer(
            'Данные не сохранены',
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.reset_state()


async def populate_plans(message: types.Message):
    await add_questions_in_plan()
    await message.answer('Вопросы для тестов сформированы')


def register_handlers_plan(dp: Dispatcher):
    dp.register_message_handler(create_plan, commands='plan')
    # dp.register_message_handler(choose_year, state=Plan.waiting_department)
    dp.register_message_handler(choose_quarter, state=Plan.waiting_year)
    dp.register_message_handler(choose_themes, state=Plan.waiting_quarter)
    dp.register_message_handler(create_list_themes, state=Plan.waiting_themes)
    dp.register_message_handler(plan_save, state=Plan.waiting_confirm)
    dp.register_message_handler(populate_plans, commands='pop_plan')
