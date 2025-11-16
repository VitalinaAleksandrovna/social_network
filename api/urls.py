"""
URL маршруты для REST API
Функционал: Определение API endpoints для фронтенда и мобильных приложений
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import users, photos, messages

router = DefaultRouter()
router.register('users', users.UserViewSet, basename='user')
router.register('photos', photos.PhotoViewSet, basename='photo')
router.register('conversations', messages.ConversationViewSet, basename='conversation')

urlpatterns = [
    # API endpoints через ViewSets
    path('', include(router.urls)),

    # JWT аутентификация
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Кастомные API endpoints
    path('photos/<int:photo_id>/like/', photos.like_photo_api, name='api_like_photo'),
    #path('users/<str:username>/friends/', users.user_friends, name='api_user_friends'),
]