"""
Модели для системы личных сообщений
Функционал: Беседы между пользователями, обмен сообщениями, статусы прочтения
"""
from django.db import models
from users.models import CustomUser


class Conversation(models.Model):
    """Модель беседы между пользователями"""
    participants = models.ManyToManyField(
        CustomUser,
        related_name='conversations',
        verbose_name="Участники"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Беседа"
        verbose_name_plural = "Беседы"
        indexes = [
            models.Index(fields=['updated_at']),
        ]

    def __str__(self):
        participants_names = ", ".join([user.username for user in self.participants.all()])
        return f"Беседа: {participants_names}"

    @property
    def last_message(self):
        """Последнее сообщение в беседе"""
        return self.messages.order_by('-timestamp').first()

    def get_unread_count(self, user):
        """Количество непрочитанных сообщений для пользователя"""
        return self.messages.filter(read=False).exclude(sender=user).count()


class Message(models.Model):
    """Модель сообщения в беседе"""
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name="Беседа"
    )
    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Отправитель"
    )
    content = models.TextField(
        max_length=2000,
        verbose_name="Текст сообщения"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Время отправки"
    )
    read = models.BooleanField(
        default=False,
        verbose_name="Прочитано"
    )

    class Meta:
        ordering = ['timestamp']
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        indexes = [
            models.Index(fields=['conversation', 'timestamp']),
            models.Index(fields=['read']),
        ]

    def __str__(self):
        return f"Сообщение от {self.sender.username} ({self.timestamp})"

    def mark_as_read(self):
        """Пометить сообщение как прочитанное"""
        if not self.read:
            self.read = True
            self.save()