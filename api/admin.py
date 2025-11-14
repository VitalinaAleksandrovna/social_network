"""
Админ-панель для приложения API
Функционал: В будущем может содержать настройки API, ключи доступа и т.д.
"""
from django.contrib import admin

# Приложение API не имеет собственных моделей для админки
# Этот файл оставлен для будущего расширения функциональности

# @admin.register(APIToken)
# class APITokenAdmin(admin.ModelAdmin):
#     list_display = ('user', 'key', 'created', 'is_active')
#     list_filter = ('is_active', 'created')
#     search_fields = ('user__username', 'key')