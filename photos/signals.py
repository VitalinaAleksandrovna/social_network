"""
Сигналы для приложения Photos
Функционал: Очистка кэша при изменении фотографий
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Photo


def clear_photos_cache():
    """Очистка кэша фотографий с проверкой поддержки паттернов"""
    try:
        # Пробуем очистить по паттерну (для Redis)
        cache.delete_pattern('photos_*')
    except AttributeError:
        # Если метод не поддерживается (LocMemCache), очищаем конкретные ключи
        cache_keys_to_delete = [
            'photos_list',
            'photos_popular',
            'photos_recent',
        ]
        for key in cache_keys_to_delete:
            cache.delete(key)


@receiver(post_save, sender=Photo)
def clear_cache_on_save(sender, instance, **kwargs):
    """Очистка кэша при сохранении фотографии"""
    clear_photos_cache()


@receiver(post_delete, sender=Photo)
def clear_cache_on_delete(sender, instance, **kwargs):
    """Очистка кэша при удалении фотографии"""
    clear_photos_cache()