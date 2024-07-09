from aiogram_dialog import DialogManager
from bson.objectid import ObjectId

from config.mongo_config import articles, themes


async def get_random_article(dialog_manager: DialogManager, **middleware_data):
    article = list(articles.aggregate([{'$sample': {'size': 1}}]))[0]
    theme = themes.find_one({'code': article['theme']})['name']
    return {'title': article['title'], 'link': article['link'], 'theme': theme}


async def get_themes(dialog_manager: DialogManager, **middleware_data):
    context = dialog_manager.current_context()
    category = context.dialog_data['category']
    if category == 'choose_theme':
        queryset = articles.distinct('theme')
        data = {
            'themes': [
                (themes.find_one({'code': theme_code})['name'], theme_code)
                for theme_code in queryset
            ],
            'is_paginated': True if len(queryset) > 6 else False
        }
    else:
        data = {
            'themes': [
                (theme['name'], theme['code']) for theme in themes.find({})
            ],
            'is_paginated': True
        }
    return data


async def get_articles(dialog_manager: DialogManager, **middleware_data):
    context = dialog_manager.current_context()
    theme_code = context.dialog_data['theme_code']
    queryset = list(articles.find({'theme': theme_code}))
    return {
        'articles': [(a['title'], str(a['_id'])) for a in queryset],
        'is_paginated': True if len(queryset) > 6 else False
    }


async def get_article_url(dialog_manager: DialogManager, **middleware_data):
    context = dialog_manager.current_context()
    article_id = context.dialog_data['article_id']
    theme_code = context.dialog_data['theme_code']
    article = articles.find_one({'_id': ObjectId(article_id)})
    theme = themes.find_one({'code': theme_code})['name']
    return {
        'theme': theme,
        'title': article['title'],
        'link': article['link'],
    }
