from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from config.mongo_config import users

UNAUTHORIZED_MSG = ('Вашей учётной записи нет в базе данных бота.\n'
                    'Взаимодействие с ботом ограничено.\n'
                    'Чтобы продолжить нажмите /start')


class CheckUserMiddleware(BaseMiddleware):
    def is_legal_user(self, user_id) -> bool:
        user_check = users.find_one({'user_id': user_id})
        return True if user_check else False

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        user = data["event_from_user"]
        if event.callback_query:
            if self.is_legal_user(user.id) or event.callback_query.data in ['cond_accept', 'cond_decline']:
                return await handler(event, data)
        elif event.message:
            if self.is_legal_user(user.id) or event.message.text == '/start':
                return await handler(event, data)
        # await event.message.answer(UNAUTHORIZED_MSG)
        # return
        return await handler(event, data)
