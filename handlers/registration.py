from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from config.bot_config import bot, dp
from config.mongo_config import users
from config.telegram_config import MY_TELEGRAM_ID
from texts.initial import REGISTRATION_TEXT
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
    await Registration.waiting_department.set()


async def department_confirm(message: types.Message, state: FSMContext):
    if message.text not in DEPARTMENTS:
        await message.answer(
            'Пожалуйста, выберите службу, используя список ниже.'
        )
        return
    await state.update_data(department=message.text)
    buffer_data = await state.get_data()
    depart = buffer_data['department']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Нет', 'Да')
    await message.answer(
        text=f'Вы выбрали {depart}. Сохранить?',
        reply_markup=keyboard,
    )
    await Registration.waiting_department_confirm.set()


async def user_save(message: types.Message, state: FSMContext):
    if message.text.lower() not in ['нет', 'да']:
        await message.answer(
            'Пожалуйста, отправьте "Да" или "Нет"'
        )
        return
    if message.text.lower() == 'да':
        user = message.from_user
        user_check = users.find_one({ 'user_id':  user.id })
        buffer_data = await state.get_data()
        depart = buffer_data['department']
        if user_check is not None:
            users.update_one(
                {'user_id': user.id},
                {
                    '$set':
                    {
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'full_name': user.full_name,
                        'department': depart
                    }
                },
                upsert=False
            )
            await state.finish()
            await bot.send_message(
                chat_id=MY_TELEGRAM_ID,
                text=f'Обновлён пользователь: {depart} - {user.full_name}'
            )
        else:
            users.insert_one(
                {
                    'user_id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'full_name': user.full_name,
                    'department': depart
                }
            )
            await state.finish()
            await bot.send_message(
                chat_id=MY_TELEGRAM_ID,
                text=f'Добавлен пользователь: {depart} - {user.full_name}'
            )
        await message.answer(
            REGISTRATION_TEXT,
            reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            ('Данные не сохранены.\n'
             'Если необходимо снова пройти процедуру регистрации '
             '- нажмите /registration'),
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.reset_state()

def register_handlers_registration(dp: Dispatcher):
    dp.register_message_handler(user_registration, commands='registration')
    dp.register_message_handler(
        department_confirm,
        state=Registration.waiting_department,
    )
    dp.register_message_handler(
        user_save,
        state=Registration.waiting_department_confirm,
    )
