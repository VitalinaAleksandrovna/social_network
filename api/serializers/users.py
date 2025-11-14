"""
Сериализаторы для моделей пользователей
Функционал: Преобразование моделей Django в JSON для API
"""
from rest_framework import serializers
from users.models import CustomUser, Friendship


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра профиля"""
    full_name = serializers.ReadOnlyField()
    photos_count = serializers.IntegerField(source='photos.count', read_only=True)
    friends_count = serializers.SerializerMethodField()
    is_friend = serializers.SerializerMethodField()
    friendship_status = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'bio', 'profile_picture', 'birth_date', 'location', 'website',
            'date_joined', 'photos_count', 'friends_count', 'is_friend', 'friendship_status'
        )
        read_only_fields = ('id', 'date_joined', 'photos_count', 'friends_count')

    def get_friends_count(self, obj):
        """Количество друзей пользователя"""
        sent = Friendship.objects.filter(from_user=obj, accepted=True).count()
        received = Friendship.objects.filter(to_user=obj, accepted=True).count()
        return sent + received

    def get_is_friend(self, obj):
        """Проверка дружбы с текущим пользователем"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if request.user == obj:
                return 'self'
            return Friendship.objects.filter(
                from_user=request.user, to_user=obj, accepted=True
            ).exists() or Friendship.objects.filter(
                from_user=obj, to_user=request.user, accepted=True
            ).exists()
        return False

    def get_friendship_status(self, obj):
        """Статус дружбы с текущим пользователем"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj:
            # Проверяем исходящий запрос
            outgoing = Friendship.objects.filter(from_user=request.user, to_user=obj).first()
            if outgoing:
                return 'outgoing_pending' if not outgoing.accepted else 'friends'

            # Проверяем входящий запрос
            incoming = Friendship.objects.filter(from_user=obj, to_user=request.user).first()
            if incoming:
                return 'incoming_pending' if not incoming.accepted else 'friends'

        return 'none'


class UserListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка пользователей"""
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name', 'profile_picture_url', 'bio')

    def get_profile_picture_url(self, obj):
        """URL аватарки пользователя"""
        if obj.profile_picture:
            return obj.profile_picture.url
        return '/static/images/default-avatar.png'


class FriendshipSerializer(serializers.ModelSerializer):
    """Сериализатор для системы дружбы"""
    from_user = UserListSerializer(read_only=True)
    to_user = UserListSerializer(read_only=True)

    class Meta:
        model = Friendship
        fields = ('id', 'from_user', 'to_user', 'created', 'accepted')
        read_only_fields = ('id', 'created')