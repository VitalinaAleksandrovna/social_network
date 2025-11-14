"""
URL маршруты для приложения сообщений
Функционал: Определение endpoints для операций с сообщениями
"""
from django.urls import path
from . import views

urlpatterns = [
    # Основные маршруты
    path('inbox/', views.inbox, name='inbox'),
    path('start/', views.start_conversation, name='start_conversation'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('conversation/<int:conversation_id>/delete/', views.delete_conversation, name='delete_conversation'),
    path('send/<str:username>/', views.send_message, name='send_message'),
]