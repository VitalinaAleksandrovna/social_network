"""
Админ-панель для управления фотографиями
Функционал: Интерфейс администрирования фото, комментариев, лайков
"""
from django.contrib import admin
from .models import Photo, Comment


class CommentInline(admin.TabularInline):
    """Inline для комментариев в админке фотографий"""
    model = Comment
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('user', 'text', 'created_at')
    ordering = ('-created_at',)


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    """Админка для фотографий"""
    list_display = ('id', 'user', 'caption_preview', 'created_at', 'likes_count', 'comments_count')
    list_filter = ('created_at', 'user')
    search_fields = ('caption', 'user__username')
    readonly_fields = ('created_at', 'updated_at', 'likes_count_display')
    inlines = [CommentInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'image', 'caption')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at', 'likes_count_display')
        }),
    )

    def caption_preview(self, obj):
        """Превью описания в списке"""
        return obj.caption[:50] + '...' if len(obj.caption) > 50 else obj.caption

    caption_preview.short_description = 'Описание'

    def likes_count_display(self, obj):
        return obj.likes.count()

    likes_count_display.short_description = 'Количество лайков'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Админка для комментариев"""
    list_display = ('id', 'user', 'photo_preview', 'text_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text', 'user__username', 'photo__caption')
    readonly_fields = ('created_at',)

    def photo_preview(self, obj):
        return f"Фото {obj.photo.id} ({obj.photo.user.username})"

    photo_preview.short_description = 'Фотография'

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text

    text_preview.short_description = 'Текст комментария'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'photo')