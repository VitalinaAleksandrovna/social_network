"""
Сериализаторы для системы сообщений
Функционал: Преобразование бесед и сообщений в JSON
"""
from rest_framework import serializers
from chat.models import Conversation, Message  # ← ИЗМЕНИЛИ ЗДЕСЬ
from api.serializers.users import UserListSerializer

class MessageSerializer(serializers.ModelSerializer):
    """Сериализатор для сообщений"""
    sender = UserListSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'sender', 'content', 'timestamp', 'read')
        read_only_fields = ('id', 'timestamp', 'read')

class ConversationListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка бесед"""
    participants = UserListSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    other_participants = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ('id', 'participants', 'other_participants', 'created_at', 'updated_at', 'last_message', 'unread_count')

    def get_last_message(self, obj):
        """Последнее сообщение в беседе"""
        last_msg = obj.messages.order_by('-timestamp').first()
        if last_msg:
            return MessageSerializer(last_msg).data
        return None

    def get_unread_count(self, obj):
        """Количество непрочитанных сообщений"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(read=False).exclude(sender=request.user).count()
        return 0

    def get_other_participants(self, obj):
        """Участники беседы кроме текущего пользователя"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            other_participants = obj.participants.exclude(id=request.user.id)
            return UserListSerializer(other_participants, many=True).data
        return []

class ConversationDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра беседы"""
    participants = UserListSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    other_participants = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ('id', 'participants', 'other_participants', 'created_at', 'updated_at', 'messages')

    def get_other_participants(self, obj):
        """Участники беседы кроме текущего пользователя"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            other_participants = obj.participants.exclude(id=request.user.id)
            return UserListSerializer(other_participants, many=True).data
        return []