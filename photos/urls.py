"""
URL маршруты для приложения фотографий
Функционал: Определение endpoints для операций с фотографиями
"""
from django.urls import path
from . import views

urlpatterns = [
    # Основные маршруты
    path('', views.photo_list, name='photo_list'),
    path('upload/', views.upload_photo, name='upload_photo'),
    path('<int:photo_id>/', views.photo_detail, name='photo_detail'),
    path('<int:photo_id>/delete/', views.delete_photo, name='delete_photo'),

    # API endpoints (AJAX)
    path('<int:photo_id>/like/', views.like_photo, name='like_photo'),
]