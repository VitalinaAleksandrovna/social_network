"""
API Views для управления фотографиями
Функционал: REST endpoints для операций с фотографиями, лайками, комментариями
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count
from photos.models import Photo, Comment
from users.models import Friendship  # ← ДОБАВЛЕН ИМПОРТ
from api.serializers.photos import PhotoSerializer, PhotoCreateSerializer, CommentSerializer
from api.permissions import IsOwnerOrReadOnly


class PhotoViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с фотографиями
    Доступные действия: list, retrieve, create, update, delete
    """
    queryset = Photo.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action in ['create', 'update', 'partial_update']:
            return PhotoCreateSerializer
        return PhotoSerializer

    def get_queryset(self):
        """Оптимизация запросов с аннотациями и prefetch"""
        queryset = Photo.objects.select_related('user').prefetch_related(
            'likes', 'comments', 'comments__user'
        ).annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments')
        ).order_by('-created_at')

        # Фильтрация по пользователю если указан username
        username = self.request.query_params.get('username')
        if username:
            queryset = queryset.filter(user__username=username)

        return queryset

    def perform_create(self, serializer):
        """Автоматическое назначение пользователя при создании фото"""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Постановка/снятие лайка на фотографию"""
        photo = self.get_object()

        if photo.likes.filter(id=request.user.id).exists():
            photo.likes.remove(request.user)
            liked = False
        else:
            photo.likes.add(request.user)
            liked = True

        # Обновляем кэшированные значения
        photo.likes_count = photo.likes.count()

        return Response({
            'liked': liked,
            'likes_count': photo.likes_count,
            'photo_id': photo.id
        })

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        """Получение и создание комментариев к фотографии"""
        photo = self.get_object()

        if request.method == 'GET':
            comments = photo.comments.select_related('user').order_by('created_at')
            serializer = CommentSerializer(comments, many=True, context={'request': request})
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = CommentSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(photo=photo, user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return None

    @action(detail=False, methods=['get'])
    def my_photos(self, request):
        """Фотографии текущего пользователя"""
        photos = self.get_queryset().filter(user=request.user)

        page = self.paginate_queryset(photos)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(photos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def feed(self, request):
        """Лента фотографий (фото друзей и свои)"""
        # Получаем ID друзей
        sent_friends = Friendship.objects.filter(
            from_user=request.user, accepted=True
        ).values_list('to_user_id', flat=True)

        received_friends = Friendship.objects.filter(
            to_user=request.user, accepted=True
        ).values_list('from_user_id', flat=True)

        friend_ids = list(sent_friends) + list(received_friends) + [request.user.id]

        photos = self.get_queryset().filter(user_id__in=friend_ids)

        page = self.paginate_queryset(photos)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(photos, many=True)
        return Response(serializer.data)


def like_photo_api(request, photo_id):
    """API endpoint для лайков (для использования вне ViewSet)"""
    if request.method == 'POST' and request.user.is_authenticated:
        photo = get_object_or_404(Photo, id=photo_id)

        if photo.likes.filter(id=request.user.id).exists():
            photo.likes.remove(request.user)
            liked = False
        else:
            photo.likes.add(request.user)
            liked = True

        return Response({
            'liked': liked,
            'likes_count': photo.likes.count(),
            'photo_id': photo_id
        })

    return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)