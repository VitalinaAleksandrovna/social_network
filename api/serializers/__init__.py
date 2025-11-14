"""
Пакет сериализаторов для API
Функционал: Экспортирует все сериализаторы для удобного импорта
"""
from .users import (
    UserProfileSerializer,
    UserListSerializer,
    FriendshipSerializer
)

from .photos import (
    PhotoSerializer,
    PhotoCreateSerializer,
    CommentSerializer
)

from .messages import (
    MessageSerializer,
    ConversationListSerializer,
    ConversationDetailSerializer
)

# Экспортируем все сериализаторы для удобного импорта
__all__ = [
    # User serializers
    'UserProfileSerializer',
    'UserListSerializer',
    'FriendshipSerializer',

    # Photo serializers  
    'PhotoSerializer',
    'PhotoCreateSerializer',
    'CommentSerializer',

    # Message serializers
    'MessageSerializer',
    'ConversationListSerializer',
    'ConversationDetailSerializer',
]


# Дополнительные утилиты для сериализаторов
def get_serializer_fields(serializer_class):
    """Возвращает список полей сериализатора"""
    return list(serializer_class().get_fields().keys())


def create_serializer_context(request):
    """Создает контекст для сериализатора"""
    return {'request': request}