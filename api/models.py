"""
Модели для приложения API
Функционал: В будущем может содержать модели для управления API (токены, квоты и т.д.)
"""
from django.db import models

# Приложение API использует сериализаторы для моделей из других приложений
# Этот файл оставлен для будущего расширения функциональности

# class APIToken(models.Model):
#     """Модель для API токенов аутентификации"""
#     user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
#     key = models.CharField(max_length=40, unique=True)
#     created = models.DateTimeField(auto_now_add=True)
#     is_active = models.BooleanField(default=True)
#     
#     def __str__(self):
#         return f"API Token for {self.user.username}"