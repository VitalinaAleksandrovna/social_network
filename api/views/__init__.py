"""
Пакет представлений для API
Функционал: Экспортирует все ViewSets и функции для удобного импорта
"""
from .users import UserViewSet
from .photos import PhotoViewSet, like_photo_api
from .messages import ConversationViewSet  # ← ОСТАЕТСЯ ТАК ЖЕ

# Экспортируем все ViewSets и функции
__all__ = [
    'UserViewSet',
    'PhotoViewSet',
    'like_photo_api',
    'ConversationViewSet',
]

# Дополнительные утилиты для views
def get_viewset_actions(viewset_class):
    """Возвращает список кастомных действий ViewSet"""
    actions = []
    for attr_name in dir(viewset_class):
        attr = getattr(viewset_class, attr_name)
        if hasattr(attr, 'mapping'):
            actions.append(attr_name)
    return actions

def get_api_endpoints(router):
    """Возвращает список всех API endpoints из router"""
    endpoints = []
    for prefix, viewset, basename in router.registry:
        endpoints.append({
            'prefix': prefix,
            'viewset': viewset.__name__,
            'basename': basename
        })
    return endpoints