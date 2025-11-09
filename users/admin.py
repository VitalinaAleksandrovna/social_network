"""
Админ-панель для управления пользователями
Функционал: Интерфейс администрирования пользователей и дружбы
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Friendship


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Админка для кастомной модели пользователя"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('bio', 'profile_picture', 'birth_date', 'location', 'website')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('email', 'bio', 'profile_picture')
        }),
    )


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    """Админка для системы дружбы"""
    list_display = ('from_user', 'to_user', 'created', 'accepted')
    list_filter = ('accepted', 'created')
    search_fields = ('from_user__username', 'to_user__username')
    readonly_fields = ('created',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('from_user', 'to_user')