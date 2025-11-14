"""
Тесты для приложения API
Функционал: Unit tests и integration tests для REST API endpoints
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import CustomUser
from photos.models import Photo


class APITestBase(APITestCase):
    """Базовый класс для тестов API"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = CustomUser.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )

        # Создаем тестовую фотографию
        self.photo = Photo.objects.create(
            user=self.user,
            caption='Test photo caption'
        )
        # Заглушка для изображения - в реальном тесте нужно использовать SimpleUploadedFile
        # self.photo.image = SimpleUploadedFile(...)


class UserAPITests(APITestBase):
    """Тесты для API пользователей"""

    def test_get_user_list(self):
        """Тест получения списка пользователей"""
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Два пользователя в базе

    def test_get_user_profile(self):
        """Тест получения профиля пользователя"""
        url = reverse('user-detail', args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_get_current_user_profile(self):
        """Тест получения профиля текущего пользователя"""
        self.client.force_authenticate(user=self.user)
        url = reverse('user-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')


class PhotoAPITests(APITestBase):
    """Тесты для API фотографий"""

    def test_get_photo_list(self):
        """Тест получения списка фотографий"""
        url = reverse('photo-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Одна фотография в базе

    def test_get_photo_detail(self):
        """Тест получения деталей фотографии"""
        url = reverse('photo-detail', args=[self.photo.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['caption'], 'Test photo caption')

    def test_like_photo_authenticated(self):
        """Тест лайка фотографии аутентифицированным пользователем"""
        self.client.force_authenticate(user=self.user)
        url = reverse('api_like_photo', args=[self.photo.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['liked'])
        self.assertEqual(response.data['likes_count'], 1)

    def test_like_photo_unauthenticated(self):
        """Тест лайка фотографии неаутентифицированным пользователем"""
        url = reverse('api_like_photo', args=[self.photo.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticationTests(APITestBase):
    """Тесты аутентификации API"""

    def test_jwt_token_obtain(self):
        """Тест получения JWT токена"""
        url = reverse('token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_jwt_token_refresh(self):
        """Тест обновления JWT токена"""
        # Сначала получаем токен
        url = reverse('token_obtain_pair')
        data = {'username': 'testuser', 'password': 'testpass123'}
        token_response = self.client.post(url, data)
        refresh_token = token_response.data['refresh']

        # Затем обновляем его
        url = reverse('token_refresh')
        data = {'refresh': refresh_token}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class PermissionTests(APITestBase):
    """Тесты прав доступа API"""

    def test_photo_delete_owner(self):
        """Тест удаления фотографии владельцем"""
        self.client.force_authenticate(user=self.user)
        url = reverse('photo-detail', args=[self.photo.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_photo_delete_non_owner(self):
        """Тест удаления фотографии не владельцем"""
        self.client.force_authenticate(user=self.other_user)
        url = reverse('photo-detail', args=[self.photo.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class APIMetricsTests(TestCase):
    """Тесты для метрик API"""

    def test_api_version_endpoint(self):
        """Тест endpoint'а версии API"""
        # Этот тест проверяет что API отвечает на базовые запросы
        from api.views import get_api_version
        version = get_api_version()
        self.assertEqual(version, "1.0.0")


# Дополнительные тестовые утилиты
class APIUtils:
    """Утилиты для тестирования API"""

    @staticmethod
    def create_test_image():
        """Создает тестовое изображение для загрузки"""
        from io import BytesIO
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile

        image = Image.new('RGB', (100, 100), color='red')
        image_io = BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)

        return SimpleUploadedFile(
            'test_image.jpg',
            image_io.getvalue(),
            content_type='image/jpeg'
        )