"""
Сигналы для приложения чата
Функционал: Автоматические действия при событиях в системе сообщений
"""
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.core.cache import cache
from .models import Message, Conversation


@receiver(post_save, sender=Message)
def update_conversation_timestamp(sender, instance, created, **kwargs):
    """Обновление времени беседы при новом сообщении"""
    if created:
        instance.conversation.save()  # Это обновит updated_at


@receiver(post_save, sender=Message)
def clear_conversations_cache(sender, instance, **kwargs):
    """Очистка кэша бесед при изменении сообщений"""
    cache.delete_pattern(f'conversations_{instance.conversation.id}_*')


@receiver(m2m_changed, sender=Conversation.participants.through)
def clear_participants_cache(sender, instance, action, **kwargs):
    """Очистка кэша при изменении участников беседы"""
    if action in ['post_add', 'post_remove', 'post_clear']:
        for user in instance.participants.all():
            cache.delete(f'user_{user.id}_conversations')