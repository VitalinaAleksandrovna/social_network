"""
Сериализаторы для моделей фотографий
Функционал: Преобразование фото и комментариев в JSON
"""
from rest_framework import serializers
from photos.models import Photo, Comment
from api.serializers.users import UserListSerializer


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев"""
    user = UserListSerializer(read_only=True)
    user_can_delete = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'user', 'text', 'created_at', 'user_can_delete')
        read_only_fields = ('id', 'created_at')

    def get_user_can_delete(self, obj):
        """Может ли текущий пользователь удалить комментарий"""
        request = self.context.get('request')
        return request and request.user.is_authenticated and (
                request.user == obj.user or request.user == obj.photo.user
        )


class PhotoSerializer(serializers.ModelSerializer):
    """Сериализатор для фотографий"""
    user = UserListSerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    user_can_edit = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Photo
        fields = (
            'id', 'user', 'image', 'image_url', 'caption', 'created_at',
            'likes_count', 'comments_count', 'is_liked', 'user_can_edit', 'comments'
        )
        read_only_fields = ('id', 'created_at', 'user')

    def get_is_liked(self, obj):
        """Проверка лайка от текущего пользователя"""
        request = self.context.get('request')
        return request and request.user.is_authenticated and obj.likes.filter(id=request.user.id).exists()

    def get_user_can_edit(self, obj):
        """Может ли текущий пользователь редактировать фото"""
        request = self.context.get('request')
        return request and request.user.is_authenticated and request.user == obj.user

    def get_image_url(self, obj):
        """URL изображения"""
        if obj.image:
            return obj.image.url
        return None


class PhotoCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания фотографий"""

    class Meta:
        model = Photo
        fields = ('image', 'caption')

    def create(self, validated_data):
        """Создание фото с автоматическим назначением пользователя"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)