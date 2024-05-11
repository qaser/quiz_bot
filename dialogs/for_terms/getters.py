from aiogram_dialog import DialogManager
from bson.objectid import ObjectId

from dialogs.for_terms.states import Terms
from config.mongo_config import terms, themes


async def get_themes(dialog_manager: DialogManager, **middleware_data):
    queryset = terms.distinct('theme')
    data = {
        'themes': [
            (themes.find_one({'code': theme_code})['name'], theme_code)
            for theme_code in queryset
        ],
    }
    return data


async def get_terms(dialog_manager: DialogManager, **middleware_data):
    theme_code = dialog_manager.current_context().dialog_data.get('theme_code')
    if not theme_code:
        await dialog_manager.event.answer('Сначала выберите тему')
        await dialog_manager.switch_to(Terms.select_themes)
        return
    queryset = list(terms.find({'theme': theme_code}))
    data = {'terms': [(term['name'], term['_id']) for term in queryset]}
    return data


async def get_description(dialog_manager: DialogManager, **middleware_data):
    term_id = dialog_manager.current_context().dialog_data['term_id']
    term_description = terms.find_one({'_id': ObjectId(term_id)}).get('description')
    data = {'term': term_description}
    return data
