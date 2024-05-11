import datetime as dt
from aiogram import Router

from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from config.bot_config import dp
from config.mongo_config import users
from config.telegram_config import PASSWORD
import utils.constants as const

router = Router()


class PasswordCheck(StatesGroup):
    password = State()


@dp.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    check_user = users.find_one({'user_id': user_id})
    if check_user is not None:
        await message.answer(const.START_TEXT)
    else:
        await message.answer(const.PASS_TEXT)
        await state.update_data(trying=3)
        await state.update_data(unblock_date=dt.datetime.now())
        await state.set_state(PasswordCheck.password)


@dp.message(PasswordCheck.password)
async def check_password(message: Message, state: FSMContext):
    state_data = await state.get_data()
    unblock_date = state_data.get('unblock_date')
    if unblock_date < dt.datetime.now():
        user = message.from_user
        if message.text == PASSWORD:
            await message.answer(f'Пароль принят\n{const.START_TEXT}')
            users.insert_one(
                {
                    'user_id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'full_name': user.full_name,
                    'is_admin': False
                }
            )
            await state.clear()
        else:
            trying = state_data['trying'] - 1
            await state.update_data(trying=trying)
            if trying <= 0:
                unblock_date = dt.datetime.now() + dt.timedelta(minutes=5)
                await state.update_data(unblock_date=unblock_date)
                await state.update_data(trying=3)
                await message.answer(f'Пароль неверный. Попыток не осталось, попробуйте через 5 минут')
            else:
                await message.answer(f'Пароль неверный. Осталось попыток: {trying}')
                return
    else:
        return
