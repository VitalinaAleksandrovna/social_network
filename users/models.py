"""
Модели для управления пользователями и друзьями
Функционал: Кастомный пользователь, система друзей, профили
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone  # ПРАВИЛЬНЫЙ ИМПОРТ


class CustomUser(AbstractUser):
    """Расширенная модель пользователя с дополнительными полями"""
    bio = models.TextField(max_length=500, blank=True, verbose_name="О себе")
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        verbose_name="Аватарка"
    )
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата рождения")
    location = models.CharField(max_length=100, blank=True, verbose_name="Местоположение")
    website = models.URLField(blank=True, verbose_name="Веб-сайт")
    # УДАЛИТЬ эту строку - date_joined уже есть в AbstractUser
    # date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Friendship(models.Model):
    """Модель системы дружбы между пользователями"""
    from_user = models.ForeignKey(
        CustomUser,
        related_name='friendship_requests_sent',
        on_delete=models.CASCADE,
        verbose_name="От пользователя"
    )
    to_user = models.ForeignKey(
        CustomUser,
        related_name='friendship_requests_received',
        on_delete=models.CASCADE,
        verbose_name="К пользователю"
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name="Дата запроса")
    accepted = models.BooleanField(default=False, verbose_name="Принято")

    class Meta:
        unique_together = ('from_user', 'to_user')
        verbose_name = "Дружба"
        verbose_name_plural = "Дружбы"

    def __str__(self):
        status = "принята" if self.accepted else "в ожидании"
        return f"Дружба {self.from_user} -> {self.to_user} ({status})"