from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, StartMode
from bson import ObjectId

from config.bot_config import bot
from config.mongo_config import articles
from dialogs.for_articles import windows
from dialogs.for_articles.states import Articles

router = Router()
dialog =  Dialog(
    windows.category_window(),
    windows.select_themes_window(),
    windows.select_articles_window(),
    windows.article_url_window(),
    windows.new_article_window(),
    windows.input_article_name_window(),
    windows.input_article_url_window(),
    windows.random_article_window(),
    windows.save_article_window()
)


@router.message(Command('articles'))
async def articles_handler(message: Message, dialog_manager: DialogManager):
    await message.delete()
    # Important: always set `mode=StartMode.RESET_STACK` you don't want to stack dialogs
    await dialog_manager.start(Articles.select_category, mode=StartMode.RESET_STACK)


@router.callback_query(F.data.startswith('article_'))
async def article_confirm(call: CallbackQuery):
    _, article_id, result = call.data.split('_')
    article = articles.find_one({'_id': ObjectId(article_id)})
    if result == 'deny':
        await bot.send_message(
            chat_id=article['user_id'],
            text='Ваша статья отклонена'
        )
    else:
        articles.update_one(
            {'_id': ObjectId(article_id)},
            {'$set': {'is_active': True}}
        )
        await bot.send_message(
            chat_id=article['user_id'],
            text=('Ваша статья успешно прошла модерацию '
                  'и теперь доступна в приложении')
        )
    await call.message.delete_reply_markup()
