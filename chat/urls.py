from django.urls import path
from . import views

urlpatterns = [
    path('inbox/', views.messages_inbox, name='messages_inbox'),
    path('conversation/<str:username>/', views.conversation_detail, name='conversation_detail'),
    path('send/<str:username>/', views.send_message, name='send_message'),
]