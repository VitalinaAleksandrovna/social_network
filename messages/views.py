"""
Представления для системы сообщений
Функционал: Входящие, отправка сообщений, управление беседами
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.db.models import Q, Count, Max
from django.http import JsonResponse
from users.models import CustomUser
from .models import Conversation, Message
from .forms import MessageForm, NewConversationForm


@login_required
def inbox(request):
    """Список бесед пользователя"""
    conversations = Conversation.objects.filter(
        participants=request.user
    ).annotate(
        last_message_time=Max('messages__timestamp'),
        unread_count=Count('messages', filter=Q(messages__read=False) & ~Q(messages__sender=request.user))
    ).order_by('-last_message_time')

    return render(request, 'messages/inbox.html', {
        'conversations': conversations,
        'page_title': 'Входящие сообщения'
    })


@login_required
def conversation_detail(request, conversation_id):
    """Детальный просмотр беседы"""
    conversation = get_object_or_404(
        Conversation.objects.prefetch_related('participants', 'messages__sender'),
        id=conversation_id,
        participants=request.user
    )

    # Помечаем сообщения как прочитанные
    unread_messages = conversation.messages.filter(read=False).exclude(sender=request.user)
    unread_messages.update(read=True)

    # Получаем сообщения беседы
    message_list = conversation.messages.all().select_related('sender')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()

            # Обновляем время беседы
            conversation.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message_id': message.id,
                    'content': message.content,
                    'timestamp': message.timestamp.isoformat()
                })

            return redirect('conversation_detail', conversation_id=conversation.id)
    else:
        form = MessageForm()

    # Получаем собеседника (исключая текущего пользователя)
    other_participants = conversation.participants.exclude(id=request.user.id)

    return render(request, 'messages/conversation_detail.html', {
        'conversation': conversation,
        'messages': message_list,
        'other_participants': other_participants,
        'form': form
    })


@login_required
def send_message(request, username):
    """Отправка сообщения конкретному пользователю"""
    recipient = get_object_or_404(CustomUser, username=username)

    if request.user == recipient:
        django_messages.error(request, "Нельзя отправить сообщение самому себе")
        return redirect('inbox')

    # Находим существующую беседу или создаем новую
    conversation = Conversation.objects.filter(participants=request.user).filter(participants=recipient).first()

    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, recipient)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()

            django_messages.success(request, f"Сообщение отправлено {recipient.username}")
            return redirect('conversation_detail', conversation_id=conversation.id)
    else:
        form = MessageForm()

    return render(request, 'messages/send_message.html', {
        'form': form,
        'recipient': recipient,
        'conversation': conversation
    })


@login_required
def start_conversation(request):
    """Начало новой беседы"""
    if request.method == 'POST':
        form = NewConversationForm(request.POST)
        if form.is_valid():
            recipient_username = form.cleaned_data['recipient_username']
            message_content = form.cleaned_data['message']

            try:
                recipient = CustomUser.objects.get(username=recipient_username)

                if request.user == recipient:
                    django_messages.error(request, "Нельзя начать беседу с самим собой")
                    return redirect('start_conversation')

                # Находим или создаем беседу
                conversation = Conversation.objects.filter(
                    participants=request.user
                ).filter(
                    participants=recipient
                ).first()

                if not conversation:
                    conversation = Conversation.objects.create()
                    conversation.participants.add(request.user, recipient)

                # Создаем первое сообщение
                if message_content.strip():
                    Message.objects.create(
                        conversation=conversation,
                        sender=request.user,
                        content=message_content.strip()
                    )

                django_messages.success(request, f"Беседа с {recipient.username} начата")
                return redirect('conversation_detail', conversation_id=conversation.id)

            except CustomUser.DoesNotExist:
                form.add_error('recipient_username', 'Пользователь с таким именем не найден')
    else:
        form = NewConversationForm()

    return render(request, 'messages/start_conversation.html', {
        'form': form,
        'page_title': 'Новая беседа'
    })


@login_required
def delete_conversation(request, conversation_id):
    """Удаление беседы"""
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)

    if request.method == 'POST':
        # Удаляем пользователя из беседы (не саму беседу, чтобы у других участников осталась)
        conversation.participants.remove(request.user)
        django_messages.success(request, "Беседа удалена")
        return redirect('inbox')

    return render(request, 'messages/confirm_delete.html', {
        'conversation': conversation
    })