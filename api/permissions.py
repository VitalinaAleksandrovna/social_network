"""
Кастомные permissions для API
Функционал: Дополнительные проверки прав доступа для различных операций
"""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение на изменение только владельцу объекта.
    Чтение разрешено всем.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем GET, HEAD, OPTIONS запросы
        if request.method in permissions.SAFE_METHODS:
            return True

        # Запись разрешена только владельцу
        return obj.user == request.user


class IsMessageParticipant(permissions.BasePermission):
    """
    Разрешение только для участников беседы.
    """

    def has_object_permission(self, request, view, obj):
        return request.user in obj.participants.all()


class IsSenderOrReadOnly(permissions.BasePermission):
    """
    Разрешение на изменение только отправителю сообщения.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем GET, HEAD, OPTIONS запросы
        if request.method in permissions.SAFE_METHODS:
            return True

        # Запись разрешена только отправителю
        return obj.sender == request.user


class IsFriendOrReadOnly(permissions.BasePermission):
    """
    Разрешение на определенные действия только друзьям.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем GET, HEAD, OPTIONS запросы
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для определенных действий проверяем дружбу
        from users.models import Friendship
        is_friend = Friendship.objects.filter(
            from_user=request.user, to_user=obj, accepted=True
        ).exists() or Friendship.objects.filter(
            from_user=obj, to_user=request.user, accepted=True
        ).exists()

        return is_friend