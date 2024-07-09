import datetime as dt

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import DialogManager

from config.bot_config import bot
from config.mongo_config import articles
from config.telegram_config import ADMIN_TELEGRAM_ID
from dialogs.for_articles.states import Articles


async def on_main_menu(callback, widget, manager: DialogManager):
    await manager.switch_to(Articles.select_category)


async def on_chosen_themes(callback, widget, manager: DialogManager):
    context = manager.current_context()
    context.dialog_data.update(category=widget.widget_id)
    await manager.switch_to(Articles.select_themes)


async def on_theme_done(callback, widget, manager: DialogManager, theme_code):
    context = manager.current_context()
    context.dialog_data.update(theme_code=theme_code)
    if context.dialog_data['category'] == 'choose_theme':
        await manager.switch_to(Articles.select_articles)
    else:
        await manager.switch_to(Articles.input_article_name)


async def on_articles_name(callback, widget, manager: DialogManager, article_id):
    context = manager.current_context()
    context.dialog_data.update(article_id=article_id)
    await manager.switch_to(Articles.article_url)


async def on_new_article(callback, widget, manager: DialogManager):
    await manager.switch_to(Articles.article_rules)


async def on_save_article_name(callback, widget, manager: DialogManager, article_name):
    context = manager.current_context()
    context.dialog_data.update(article_name=article_name)
    await manager.switch_to(Articles.input_article_url)


async def on_save_article(callback, widget, manager: DialogManager, article_url):
    context = manager.current_context()
    user = manager.event.from_user
    name = context.dialog_data['article_name']
    article_id = articles.insert_one({
        'theme': context.dialog_data['theme_code'],
        'user_id': user.id,
        'link': article_url,
        'tags': [],
        'title': name,
        'rating': 0,
        'pub_date': dt.datetime.today(),
        'is_active': False
    }).inserted_id
    kb = InlineKeyboardBuilder()
    kb.button(text='Отклонить', callback_data=f'article_{article_id}_deny')
    kb.button(text='Принять', callback_data=f'article_{article_id}_accept')
    kb.adjust(2)
    await bot.send_message(
        chat_id=ADMIN_TELEGRAM_ID,
        text=(f'Получена новая статья:\n<b>Автор:<b/> {user.username}\n'
              f'<b>Название статьи:</b> {name}\n{article_url}'),
        reply_markup=kb.as_markup()
    )
    await manager.switch_to(Articles.article_save_done)


async def on_random_article(callback, widget, manager: DialogManager):
    await manager.switch_to(Articles.random_article)
