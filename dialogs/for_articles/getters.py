from aiogram_dialog import DialogManager
from bson.objectid import ObjectId

from config.mongo_config import articles, themes
from dialogs.for_articles.states import Articles


async def get_random_article(dialog_manager: DialogManager, **middleware_data):
    article = list(articles.aggregate([{'$sample': {'size': 1}}]))[0]
    return {'title': article['title'], 'link': article['link']}


async def get_themes(dialog_manager: DialogManager, **middleware_data):
    queryset = articles.distinct('theme')
    data = {
        'themes': [
            (themes.find_one({'code': theme_code})['name'], theme_code)
            for theme_code in queryset
        ],
    }
    return data
