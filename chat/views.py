from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Conversation, Message
from .forms import MessageForm
from users.models import CustomUser


@login_required
def messages_inbox(request):
    """Список диалогов"""
    conversations = Conversation.objects.filter(
        participants=request.user
    ).prefetch_related('participants', 'messages').order_by('-updated_at')

    return render(request, 'chat/inbox.html', {
        'conversations': conversations
    })


@login_required
def conversation_detail(request, username):
    """Диалог с конкретным пользователем"""
    other_user = get_object_or_404(CustomUser, username=username)

    # Находим или создаем диалог
    conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).distinct().first()

    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()

            # Обновляем время последнего обновления диалога
            conversation.save()
            return redirect('conversation_detail', username=username)
    else:
        form = MessageForm()

    # Помечаем сообщения как прочитанные
    conversation.messages.filter(
        sender=other_user,
        is_read=False
    ).update(is_read=True)

    messages_list = conversation.messages.all()

    return render(request, 'chat/conversation.html', {
        'conversation': conversation,
        'other_user': other_user,
        'messages': messages_list,
        'form': form
    })


@login_required
def send_message(request, username):
    """Быстрая отправка сообщения"""
    if request.method == 'POST':
        other_user = get_object_or_404(CustomUser, username=username)

        # Находим или создаем диалог
        conversation = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=other_user
        ).distinct().first()

        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.add(request.user, other_user)

        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()

            conversation.save()
            messages.success(request, 'Сообщение отправлено!')

    return redirect('user_profile', username=username)