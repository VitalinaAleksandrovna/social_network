"""
Админ-панель для управления сообщениями
Функционал: Интерфейс администрирования бесед и сообщений
"""
from django.contrib import admin
from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    """Inline для сообщений в админке бесед"""
    model = Message
    extra = 0
    readonly_fields = ('timestamp',)
    fields = ('sender', 'content', 'timestamp', 'read')
    ordering = ('-timestamp',)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Админка для бесед"""
    list_display = ('id', 'participants_list', 'created_at', 'updated_at', 'message_count')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('participants__username',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [MessageInline]
    filter_horizontal = ('participants',)

    def participants_list(self, obj):
        return ", ".join([user.username for user in obj.participants.all()])

    participants_list.short_description = 'Участники'

    def message_count(self, obj):
        return obj.messages.count()

    message_count.short_description = 'Сообщений'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('participants')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Админка для сообщений"""
    list_display = ('id', 'sender', 'conversation_preview', 'content_preview', 'timestamp', 'read')
    list_filter = ('read', 'timestamp', 'sender')
    search_fields = ('content', 'sender__username', 'conversation__participants__username')
    readonly_fields = ('timestamp',)
    list_editable = ('read',)

    def conversation_preview(self, obj):
        participants = ", ".join([user.username for user in obj.conversation.participants.all()])
        return f"Беседа: {participants}"

    conversation_preview.short_description = 'Беседа'

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    content_preview.short_description = 'Содержание'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sender', 'conversation')