"""
Главный файл views для приложения API
Функционал: Импортирует и предоставляет все API ViewSets и функции
"""
from .views.users import UserViewSet
from .views.photos import PhotoViewSet, like_photo_api
from .views.messages import ConversationViewSet

# Экспортируем все ViewSets и функции для использования в urls.py
__all__ = [
    'UserViewSet',
    'PhotoViewSet', 
    'like_photo_api',
    'ConversationViewSet',
]

# Дополнительные utility функции для API
def get_api_version():
    """Возвращает версию API"""
    return "1.0.0"

def get_api_documentation_url():
    """Возвращает URL документации API"""
    return "/api/docs/"

# В будущем здесь могут быть:
# - API health checks
# - API метрики
# - Документация API
# - Versioning helpers