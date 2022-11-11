# from config.pyrogram_config import app
import asyncio

from pyrogram import Client
from pyrogram.types import ChatPrivileges

API_HASH='e962db8176f1c7b85eab97ac8acde1e3'
API_ID=14823047
TITLE='History grabber'

# from config.telegram_config import API_HASH, API_ID, TITLE


app = Client(TITLE, api_id=API_ID, api_hash=API_HASH)


async def create_group():
    async with app:
        user_id = 1835903546
        group_name = f'Тестовая группа'
        group = await app.create_supergroup(group_name)
        group_id = group.id
        # await group.add_members(1835903546)
        # await app.add_chat_members(group_id, user_id)
        # await app.promote_chat_member(
        #     chat_id= group_id,
        #     user_id=user_id,
        #     privileges=ChatPrivileges(
        #         can_manage_chat=True,
        #         can_delete_messages=True,
        #         can_manage_video_chats=True,
        #         can_restrict_members=True,
        #         can_promote_members=True,
        #         can_change_info=True,
        #         can_post_messages=True,
        #         can_edit_messages=True,
        #         can_invite_users=True,
        #         can_pin_messages=True,
        #         is_anonymous=False
        #     )
        # )
        # await app.leave_chat(group_id)


# create_group()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(create_group()) # передайте точку входа
    finally:
        # действия на выходе, если требуются
        pass