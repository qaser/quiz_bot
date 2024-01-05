from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config.bot_config import bot
from config.mongo_config import users
from config.telegram_config import ADMIN_TELEGRAM_ID
from texts.initial import REGISTRATION_TEXT
from utils.constants import DEPARTMENTS
import keyboards.for_registration as kb


router = Router()

class Registration(StatesGroup):
    department = State()
    confirm = State()


@router.message(Command('registration'))
async def user_registration(message: Message, state: FSMContext):
    await bot.send_message(
        chat_id=message.from_user.id,
        text=('ВНИМАНИЕ! Прочтите Пользовательское соглашение '
              'https://telegra.ph/Polzovatelskoe-soglashenie-01-05-5\n'
              'Пройдя регистрацию Вы соглашаетесь на обработку '
              'следующих персональных данных:\n'
              '1. Идентификационный номер пользователя Telegram,\n'
              '2. Имя пользователя Telegram,\n'
              '3. Место Вашей работы без привязки к организации.\n'
              'Если Вы не согласны с данными условиями, то прервите регистрацию '
              'нажав /reset\n\nЕсли Вы согласны, то '
              'выберите наименование службы, в которой Вы работаете.'),
        reply_markup=kb.get_departments_kb()
    )
    await state.set_state(Registration.department)


@router.message(Registration.department)
async def department_confirm(message: Message, state: FSMContext):
    if message.text not in DEPARTMENTS:
        await message.answer(
            'Пожалуйста, выберите службу, используя список ниже.'
        )
        return
    await state.update_data(department=message.text)
    buffer_data = await state.get_data()
    depart = buffer_data['department']
    await message.answer(
        text=f'Вы выбрали {depart}. Сохранить?',
        reply_markup=kb.get_yes_no_kb(),
    )
    await state.set_state(Registration.confirm)


@router.message(Registration.confirm)
async def user_save(message: Message, state: FSMContext):
    if message.text.lower() not in ['нет', 'да']:
        await message.answer('Пожалуйста, отправьте "Да" или "Нет"')
        return
    if message.text.lower() == 'да':
        user = message.from_user
        user_check = users.find_one({'user_id':  user.id})
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
            await state.clear()
            await bot.send_message(
                chat_id=ADMIN_TELEGRAM_ID,
                text=f'Обновлён пользователь:\n{depart} - {user.full_name}'
            )
        else:
            users.insert_one(
                {
                    'user_id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'full_name': user.full_name,
                    'department': depart,
                    'is_admin': 'false'
                }
            )
            await state.clear()
            await bot.send_message(
                chat_id=ADMIN_TELEGRAM_ID,
                text=f'Добавлен пользователь:\n{depart} - {user.full_name}'
            )
        await message.answer(
            REGISTRATION_TEXT,
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            ('Данные не сохранены.\n'
             'Если необходимо снова пройти процедуру регистрации '
             '- нажмите /registration'),
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
