from django.apps import AppConfig

class ChatConfig(AppConfig):  # ← ПРАВИЛЬНОЕ ИМЯ КЛАССА
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'
    verbose_name = 'Личные сообщения'

    def ready(self):
        try:
            import chat.signals  # ← ПРАВИЛЬНЫЙ ПУТЬ
        except ImportError:
            pass