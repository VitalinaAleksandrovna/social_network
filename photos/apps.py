"""
Конфигурация приложения Photos
Функционал: Настройки приложения, сигналы, кастомные команды
"""
from django.apps import AppConfig


class PhotosConfig(AppConfig):
    """Конфигурация приложения Photos"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'photos'
    verbose_name = 'Фотографии'

    def ready(self):
        """Инициализация приложения - подключение сигналов"""
        # Импортируем сигналы для обработки событий фотографий
        try:
            import photos.signals  # noqa: F401
        except ImportError:
            # Сигналы могут быть не реализованы
            pass