import functools
import inspect

from config.bot_config import bot
from config.mongo_config import users
from config.telegram_config import ADMIN_TELEGRAM_ID


# декоратор проверки регистрации пользователя
def registration_check(f):
    @functools.wraps(f)
    async def wrapped_func(*args, **kwargs):
        func_args = inspect.getcallargs(f, *args, **kwargs)
        user_id = func_args['message'].from_user.id
        if users.find_one({'user_id': user_id}) is None:
            await bot.send_message(
                user_id,
                ('Вы не зарегистрированы в системе.\n'
                 'Пройдите регистрацию /registration')
            )
        else:
            return await f(*args, **kwargs)
    return wrapped_func


def admin_check(f):
    @functools.wraps(f)
    async def wrapped_func(*args, **kwargs):
        func_args = inspect.getcallargs(f, *args, **kwargs)
        user_id = func_args['message'].from_user.id
        user = users.find_one({'user_id': user_id})
        if user.get('is_admin') == 'false':
            await bot.send_message(user_id, 'Вам не доступна эта команда')
        else:
            return await f(*args, **kwargs)
    return wrapped_func


def superuser_check(f):
    @functools.wraps(f)
    async def wrapped_func(*args, **kwargs):
        func_args = inspect.getcallargs(f, *args, **kwargs)
        user_id = func_args['message'].from_user.id
        if user_id != ADMIN_TELEGRAM_ID:
            await bot.send_message(user_id, 'Вам не доступна эта команда')
        else:
            return await f(*args, **kwargs)
    return wrapped_func
