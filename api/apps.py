"""
Конфигурация приложения API
Функционал: Настройки приложения, сигналы, кастомные команды
"""
from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Конфигурация приложения API"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'REST API'

    def ready(self):
        """Инициализация приложения"""
        # Импортируем сигналы
        try:
            import api.signals  # noqa: F401
        except ImportError:
            pass