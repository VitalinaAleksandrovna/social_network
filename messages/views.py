from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Conversation, Message
from .forms import MessageForm


@login_required
def inbox(request):
    conversations = Conversation.objects.filter(participants=request.user)
    return render(request, 'messages/inbox.html', {'conversations': conversations})


@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            return redirect('conversation_detail', conversation_id=conversation.id)

    messages = conversation.messages.all().order_by('timestamp')
    form = MessageForm()

    return render(request, 'messages/conversation_detail.html', {
        'conversation': conversation,
        'messages': messages,
        'form': form
    })


@login_required
def send_message(request, recipient_id):
    recipient = get_object_or_404(User, id=recipient_id)

    # Находим или создаем беседу
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
            return redirect('conversation_detail', conversation_id=conversation.id)

    form = MessageForm()
    return render(request, 'messages/send_message.html', {
        'form': form,
        'recipient': recipient,
        'conversation': conversation
    })
