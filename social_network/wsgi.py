"""
WSGI config для Social Network проекта.

Функционал: Конфигурация для WSGI серверов (Gunicorn, uWSGI)
Используется для:
- Production развертывание
- Традиционные синхронные серверы
- Совместимость с большинством хостингов
"""

import os
from django.core.wsgi import get_wsgi_application

# Настройка переменных окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_network.settings')

# Получаем WSGI приложение Django
application = get_wsgi_application()

# Дополнительные настройки для production:
# from whitenoise import WhiteNoise
# application = WhiteNoise(application, root='/path/to/static/files')

# Для Sentry мониторинга (раскомментировать если нужно):
# from sentry_sdk.integrations.wsgi import SentryWsgiMiddleware
# application = SentryWsgiMiddleware(application)