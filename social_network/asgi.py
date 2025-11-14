"""
ASGI config для Social Network проекта.

Функционал: Конфигурация для асинхронных серверов (Daphne, Uvicorn)
Используется для:
- WebSocket соединений (чат в реальном времени)
- Асинхронные запросы
- Production серверы
"""

import os
from django.core.asgi import get_asgi_application

# Настройка переменных окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_network.settings')

# Получаем ASGI приложение Django
application = get_asgi_application()

# В будущем можно добавить WebSocket routing для чата в реальном времени:
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# import messages.routing
#
# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             messages.routing.websocket_urlpatterns
#         )
#     ),
# })