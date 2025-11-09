"""
Главные URL маршруты проекта
Функционал: Связывает все приложения через URL patterns
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),      # Маршруты пользователей
    path('photos/', include('photos.urls')),    # Маршруты фотографий
    path('messages/', include('messages.urls')), # Маршруты сообщений
    path('api/', include('api.urls')),          # API endpoints
    path('', include('photos.urls')),           # Главная страница -> фото
]

# Обслуживание медиафайлов в разработке
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)