"""
Модели для системы фотографий и взаимодействий
Функционал: Фотографии, лайки, комментарии
"""
from django.db import models
from users.models import CustomUser


class Photo(models.Model):
    """Модель фотографии с метаданными"""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name="Пользователь"
    )
    image = models.ImageField(
        upload_to='photos/%Y/%m/%d/',
        verbose_name="Изображение"
    )
    caption = models.TextField(
        blank=True,
        verbose_name="Описание",
        help_text="Добавьте описание к фотографии"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    likes = models.ManyToManyField(
        CustomUser,
        related_name='liked_photos',
        blank=True,
        verbose_name="Лайки"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Фотография"
        verbose_name_plural = "Фотографии"

    def __str__(self):
        return f"Фото {self.id} от {self.user.username}"

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.count()


class Comment(models.Model):
    """Модель комментария к фотографии"""
    photo = models.ForeignKey(
        Photo,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Фотография"
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    text = models.TextField(
        verbose_name="Текст комментария",
        help_text="Максимум 1000 символов",
        max_length=1000
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата комментария"
    )

    class Meta:
        ordering = ['created_at']
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return f"Комментарий {self.user.username} к фото {self.photo.id}"