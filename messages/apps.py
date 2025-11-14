"""
Конфигурация приложения Messages
Функционал: Настройки приложения, сигналы, кастомные команды
"""
from django.apps import AppConfig


class MessagesConfig(AppConfig):
    """Конфигурация приложения Messages"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'messages'
    verbose_name = 'Личные сообщения'

    def ready(self):
        """Инициализация приложения - подключение сигналов"""
        # Импортируем сигналы для обработки событий сообщений
        try:
            import messages.signals  # noqa: F401
        except ImportError:
            # Сигналы могут быть не реализованы
            pass