"""
Конфигурация приложения Users
Функционал: Настройки приложения, сигналы, кастомные команды
"""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Конфигурация приложения Users"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'Пользователи'

    def ready(self):
        """Инициализация приложения - подключение сигналов"""
        # Импортируем сигналы для обработки событий пользователей
        try:
            import users.signals  # noqa: F401
        except ImportError:
            # Сигналы могут быть не реализованы
            pass