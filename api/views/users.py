"""
API Views для управления пользователями
Функционал: REST endpoints для операций с пользователями
"""
from django.http import JsonResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from users.models import CustomUser, Friendship
from api.serializers.users import UserProfileSerializer, UserListSerializer, FriendshipSerializer
from api.permissions import IsOwnerOrReadOnly
from django.contrib.auth.models import User


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с пользователями
    Доступные действия: list, retrieve, update (только свой профиль)
    """
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action == 'retrieve':
            return UserProfileSerializer
        return UserListSerializer

    def get_queryset(self):
        """Оптимизация запросов к базе данных"""
        queryset = super().get_queryset()
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related('photos')
        return queryset

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Получение профиля текущего пользователя"""
        serializer = UserProfileSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def send_friend_request(self, request, pk=None):
        """Отправка запроса на дружбу"""
        target_user = self.get_object()

        if request.user == target_user:
            return Response(
                {'error': 'Нельзя отправить запрос на дружбу самому себе'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверяем существующий запрос
        existing_request = Friendship.objects.filter(
            from_user=request.user, to_user=target_user
        ).first()

        if existing_request:
            return Response(
                {'error': 'Запрос на дружбу уже отправлен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Создаем новый запрос
        friendship = Friendship.objects.create(
            from_user=request.user,
            to_user=target_user
        )

        serializer = FriendshipSerializer(friendship, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def accept_friend_request(self, request, pk=None):
        """Принятие запроса на дружбу"""
        from_user = self.get_object()

        friendship = get_object_or_404(
            Friendship,
            from_user=from_user,
            to_user=request.user,
            accepted=False
        )

        friendship.accepted = True
        friendship.save()

        serializer = FriendshipSerializer(friendship, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def friends(self, request, pk=None):
        """Список друзей пользователя"""
        user = self.get_object()

        # Друзья - это принятые запросы в обе стороны
        sent_friends = Friendship.objects.filter(
            from_user=user, accepted=True
        ).select_related('to_user')

        received_friends = Friendship.objects.filter(
            to_user=user, accepted=True
        ).select_related('from_user')

        friends = []
        for friendship in sent_friends:
            friends.append(friendship.to_user)
        for friendship in received_friends:
            friends.append(friendship.from_user)

        serializer = UserListSerializer(friends, many=True, context={'request': request})
        return Response(serializer.data)

    @staticmethod
    def user_friends(username):
        """
        Получить список друзей пользователя
        """
        user = get_object_or_404(CustomUser, username=username)  # ← ИЗМЕНИТЬ User на CustomUser

        # Получаем подтвержденные дружеские связи в обе стороны
        sent_friendships = Friendship.objects.filter(
            from_user=user, accepted=True
        ).select_related('to_user')

        received_friendships = Friendship.objects.filter(
            to_user=user, accepted=True
        ).select_related('from_user')

        friends_data = []

        # Друзья из отправленных запросов
        for friendship in sent_friendships:
            friend = friendship.to_user
            friends_data.append({
                'id': friend.id,
                'username': friend.username,
                'email': friend.email,
                'date_joined': friend.date_joined.isoformat(),
            })

        # Друзья из полученных запросов
        for friendship in received_friendships:
            friend = friendship.from_user
            friends_data.append({
                'id': friend.id,
                'username': friend.username,
                'email': friend.email,
                'date_joined': friend.date_joined.isoformat(),
            })

        return JsonResponse({
            'username': username,
            'friends_count': len(friends_data),
            'friends': friends_data
        })