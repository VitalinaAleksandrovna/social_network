"""
API Views для системы сообщений
Функционал: REST endpoints для бесед и сообщений
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Max, Count
from messages.models import Conversation, Message
from api.serializers.messages import ConversationListSerializer, ConversationDetailSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с беседами
    Доступные действия: list, retrieve, create
    """
    queryset = Conversation.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action == 'retrieve':
            return ConversationDetailSerializer
        return ConversationListSerializer

    def get_queryset(self):
        """Беседы текущего пользователя с аннотациями"""
        return Conversation.objects.filter(
            participants=self.request.user
        ).annotate(
            last_message_time=Max('messages__timestamp'),
            unread_count=Count('messages', filter=Q(messages__read=False) & ~Q(messages__sender=self.request.user))
        ).order_by('-last_message_time').prefetch_related('participants', 'messages__sender')

    def perform_create(self, serializer):
        """Создание беседы с автоматическим добавлением текущего пользователя"""
        conversation = serializer.save()
        conversation.participants.add(self.request.user)

    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """Добавление участника в беседу"""
        conversation = self.get_object()
        username = request.data.get('username')

        if not username:
            return Response(
                {'error': 'Username is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from users.models import CustomUser
        try:
            user = CustomUser.objects.get(username=username)
            conversation.participants.add(user)

            # Создаем системное сообщение
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=f'{request.user.username} добавил(а) {username} в беседу',
                read=True
            )

            return Response({'status': 'Participant added'})

        except CustomUser.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Отправка сообщения в беседу"""
        conversation = self.get_object()

        # Проверяем что пользователь участник беседы
        if not conversation.participants.filter(id=request.user.id).exists():
            return Response(
                {'error': 'Not a participant of this conversation'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = MessageSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            message = serializer.save(conversation=conversation, sender=request.user)

            # Обновляем время беседы
            conversation.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Пометить все сообщения в беседе как прочитанные"""
        conversation = self.get_object()

        # Помечаем непрочитанные сообщения от других пользователей
        unread_messages = conversation.messages.filter(
            read=False
        ).exclude(sender=request.user)

        unread_messages.update(read=True)

        return Response({
            'status': 'marked as read',
            'messages_updated': unread_messages.count()
        })

    @action(detail=False, methods=['post'])
    def start_conversation(self, request):
        """Начало новой беседы с пользователем"""
        username = request.data.get('username')
        message_content = request.data.get('message', '')

        if not username:
            return Response(
                {'error': 'Username is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from users.models import CustomUser
        try:
            recipient = CustomUser.objects.get(username=username)

            if request.user == recipient:
                return Response(
                    {'error': 'Cannot start conversation with yourself'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Ищем существующую беседу
            conversation = Conversation.objects.filter(
                participants=request.user
            ).filter(
                participants=recipient
            ).first()

            if not conversation:
                conversation = Conversation.objects.create()
                conversation.participants.add(request.user, recipient)

            # Создаем первое сообщение если указано
            if message_content.strip():
                Message.objects.create(
                    conversation=conversation,
                    sender=request.user,
                    content=message_content.strip()
                )

            serializer = ConversationDetailSerializer(conversation, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except CustomUser.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )