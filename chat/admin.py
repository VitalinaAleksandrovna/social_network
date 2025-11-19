from django.contrib import admin
from .models import Conversation, Message

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'updated_at', 'participants_count']
    list_filter = ['created_at', 'updated_at']
    filter_horizontal = ['participants']
    
    def participants_count(self, obj):
        return obj.participants.count()
    participants_count.short_description = 'Участников'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'conversation', 'timestamp', 'is_read', 'content_preview']
    list_filter = ['timestamp', 'is_read', 'sender']
    search_fields = ['content', 'sender__username']
    readonly_fields = ['timestamp']
    list_editable = ['is_read']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Сообщение'