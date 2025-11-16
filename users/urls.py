from django.urls import path
from . import views

urlpatterns = [
    # Аутентификация
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Профили - ВАЖНО: конкретный маршрут ДО общего
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),

    # Система друзей
    path('friend-request/<str:username>/', views.send_friend_request, name='send_friend_request'),
    path('accept-friend/<str:username>/', views.accept_friend_request, name='accept_friend_request'),
]