from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from config.bot_config import bot, dp
from utils.constants import DEPARTMENTS


class Registration(StatesGroup):
    waiting_department = State()
    waiting_department_confirm = State()


# обработка команды /registration - сбор данных о пользователях
async def user_registration(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for dep in DEPARTMENTS:
        keyboard.add(dep)
    await bot.send_message(
        chat_id=message.from_user.id,
        text=(
            'Выберите наименование службы, в которой Вы работаете.'
        ),
        reply_markup=keyboard
    )
    # await Registration.waiting_department.set()


async def department_confirm(message: types.Message, state: FSMContext):
    if message.text not in DEPARTMENTS:
        await message.answer(
            'Пожалуйста, выберите службу, используя список ниже.'
        )
        return
    await state.update_data(department=message.text)
    buffer_data = await state.get_data()
    station = buffer_data['station']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Нет', 'Да')
    await message.answer(
        text=f'Вы выбрали {station}. Сохранить?',
        reply_markup=keyboard,
    )
    await GksManager.waiting_station_confirm.set()


async def user_save(message: types.Message, state: FSMContext):
    if message.text.lower() not in ['нет', 'да']:
        await message.answer(
            'Пожалуйста, отправьте "Да" или "Нет"'
        )
        return
    if message.text.lower() == 'да':
        buffer_data = await state.get_data()
        station = buffer_data['station']
        user = message.from_user
        station_check = users.find_one({'_id': station})
        if station_check is not None:
            users.update_one(
                {'_id': station},
                {
                    '$set':
                    {
                        'user_id': user.id,
                        'username': user.full_name
                    }
                },
                upsert=False
            )
            await message.answer(
                'Данные отправлены и сохранены.',
                reply_markup=types.ReplyKeyboardRemove()
            )
            await state.finish()
            await bot.send_message(
                chat_id=MY_TELEGRAM_ID,
                text=f'Обновлён начальник ГКС: {station}, {user.full_name}'
            )
        else:
            users.insert_one(
                {
                    '_id': station,
                    'user_id': user.id,
                    'username': user.full_name
                }
            )
            await message.answer(
                'Данные отправлены и сохранены.',
                reply_markup=types.ReplyKeyboardRemove()
            )
            await state.finish()
            await bot.send_message(
                chat_id=MY_TELEGRAM_ID,
                text=f'Добавлен начальник ГКС: {station}, {user.full_name}'
            )
    else:
        await message.answer(
            ('Данные не сохранены.\n'
             'Если необходимо отправить новые данные - нажмите /gks'),
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.reset_state()

def register_handlers_registration(dp: Dispatcher):
#     dp.register_message_handler(reset_handler, commands='reset', state='*')
    dp.register_message_handler(user_registration, commands='registration')