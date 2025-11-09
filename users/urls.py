"""
URL маршруты для приложения пользователей
Функционал: Определение endpoints для пользовательских операций
"""
from django.urls import path
from . import views

urlpatterns = [
    # Аутентификация
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Профили
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),

    # Система друзей
    path('friend-request/<str:username>/', views.send_friend_request, name='send_friend_request'),
    path('accept-friend/<str:username>/', views.accept_friend_request, name='accept_friend_request'),
]