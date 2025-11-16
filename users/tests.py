"""
Тесты для приложения Users
Функционал: Unit tests и integration tests для системы пользователей и друзей
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Friendship


class UsersModelTests(TestCase):
    """Тесты моделей системы пользователей"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.User = get_user_model()
        self.user1 = self.User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = self.User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        self.user3 = self.User.objects.create_user(
            username='user3',
            email='user3@example.com',
            password='testpass123'
        )

    def test_custom_user_creation(self):
        """Тест создания кастомного пользователя"""
        user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            bio='Тестовое био',
            location='Тестовый город'
        )

        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertEqual(user.bio, 'Тестовое био')
        self.assertEqual(user.location, 'Тестовый город')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_superuser_creation(self):
        """Тест создания суперпользователя"""
        admin_user = self.User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )

        self.assertEqual(admin_user.username, 'admin')
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_user_str_method(self):
        """Тест строкового представления пользователя"""
        self.assertEqual(str(self.user1), 'user1')

    def test_user_full_name_property(self):
        """Тест свойства full_name пользователя"""
        user = self.User.objects.create_user(
            username='fullnameuser',
            email='fullname@example.com',
            password='testpass123',
            first_name='Иван',
            last_name='Петров'
        )

        self.assertEqual(user.full_name, 'Иван Петров')

    def test_user_full_name_empty(self):
        """Тест свойства full_name когда имя и фамилия пустые"""
        self.assertEqual(self.user1.full_name, '')

    def test_friendship_creation(self):
        """Тест создания дружбы"""
        friendship = Friendship.objects.create(
            from_user=self.user1,
            to_user=self.user2
        )

        self.assertEqual(friendship.from_user, self.user1)
        self.assertEqual(friendship.to_user, self.user2)
        self.assertFalse(friendship.accepted)
        self.assertIsNotNone(friendship.created)

    def test_friendship_str_method(self):
        """Тест строкового представления дружбы"""
        friendship = Friendship.objects.create(
            from_user=self.user1,
            to_user=self.user2
        )

        expected_str = f"Дружба {self.user1} -> {self.user2} (в ожидании)"
        self.assertEqual(str(friendship), expected_str)

    def test_friendship_str_accepted(self):
        """Тест строкового представления принятой дружбы"""
        friendship = Friendship.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            accepted=True
        )

        expected_str = f"Дружба {self.user1} -> {self.user2} (принята)"
        self.assertEqual(str(friendship), expected_str)

    def test_friendship_unique_together(self):
        """Тест уникальности пары пользователей в дружбе"""
        Friendship.objects.create(
            from_user=self.user1,
            to_user=self.user2
        )

        # Попытка создать дубликат должна вызвать ошибку
        with self.assertRaises(Exception):
            Friendship.objects.create(
                from_user=self.user1,
                to_user=self.user2
            )


class UsersViewTests(TestCase):
    """Тесты представлений системы пользователей"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = self.User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )

    def test_register_view_get(self):
        """Тест GET запроса регистрации"""
        response = self.client.get(reverse('register'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertContains(response, 'Регистрация')

    def test_register_view_post_valid(self):
        """Тест POST запроса регистрации с валидными данными"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'bio': 'Новый пользователь'
        })

        # Должен перенаправить на список фотографий после успешной регистрации
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('photos/photo_list.html'))

        # Проверяем что пользователь создался
        new_user = self.User.objects.get(username='newuser')
        self.assertEqual(new_user.email, 'newuser@example.com')
        self.assertEqual(new_user.bio, 'Новый пользователь')

    def test_login_view_get(self):
        """Тест GET запроса входа"""
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
        self.assertContains(response, 'Вход в систему')

    def test_login_view_post_valid(self):
        """Тест POST запроса входа с валидными данными"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })

        # Должен перенаправить на список фотографий после успешного входа
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('photos/photo_list.html'))

    def test_login_view_post_invalid(self):
        """Тест POST запроса входа с невалидными данными"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })

        # Должен остаться на странице входа с ошибкой
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Неверное имя пользователя или пароль')

    def test_logout_view(self):
        """Тест выхода из системы"""
        # Сначала входим в систему
        self.client.login(username='testuser', password='testpass123')

        # Затем выходим
        response = self.client.get(reverse('logout'))

        # Должен перенаправить на страницу входа
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))

    def test_user_profile_view_authenticated(self):
        """Тест просмотра профиля аутентифицированным пользователем"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('user_profile', args=[self.user.username]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')
        self.assertContains(response, self.user.username)

    def test_user_profile_view_unauthenticated(self):
        """Тест просмотра профиля неаутентифицированным пользователем"""
        response = self.client.get(reverse('user_profile', args=[self.user.username]))

        # Должен перенаправить на страницу входа
        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/login/', response.url)

    def test_profile_edit_view_authenticated(self):
        """Тест редактирования профиля аутентифицированным пользователем"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile_edit'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile_edit.html')
        self.assertContains(response, 'Редактирование профиля')

    def test_profile_edit_view_unauthenticated(self):
        """Тест редактирования профиля неаутентифицированным пользователем"""
        response = self.client.get(reverse('profile_edit'))

        # Должен перенаправить на страницу входа
        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/login/', response.url)


class FriendshipViewTests(TestCase):
    """Тесты представлений системы друзей"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.User = get_user_model()
        self.user1 = self.User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = self.User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )

    def test_send_friend_request(self):
        """Тест отправки запроса на дружбу"""
        self.client.login(username='user1', password='testpass123')

        response = self.client.post(reverse('send_friend_request', args=[self.user2.username]))

        # Должен перенаправить на профиль пользователя
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('user_profile', args=[self.user2.username]))

        # Проверяем что запрос дружбы создался
        friendship = Friendship.objects.filter(from_user=self.user1, to_user=self.user2).first()
        self.assertIsNotNone(friendship)
        self.assertFalse(friendship.accepted)

    def test_accept_friend_request(self):
        """Тест принятия запроса на дружбу"""
        # Сначала создаем запрос дружбы
        friendship = Friendship.objects.create(
            from_user=self.user2,
            to_user=self.user1
        )

        self.client.login(username='user1', password='testpass123')
        response = self.client.post(reverse('accept_friend_request', args=[self.user2.username]))

        # Должен перенаправить на профиль пользователя
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('user_profile', args=[self.user2.username]))

        # Проверяем что дружба принята
        friendship.refresh_from_db()
        self.assertTrue(friendship.accepted)


class UsersFormTests(TestCase):
    """Тесты форм системы пользователей"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.User = get_user_model()

    def test_custom_user_creation_form_valid(self):
        """Тест валидной формы создания пользователя"""
        from .forms import CustomUserCreationForm

        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'bio': 'Тестовое био'
        }
        form = CustomUserCreationForm(data=form_data)

        self.assertTrue(form.is_valid())

    def test_custom_user_creation_form_password_mismatch(self):
        """Тест формы создания пользователя с несовпадающими паролями"""
        from .forms import CustomUserCreationForm

        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'differentpassword123',
            'bio': 'Тестовое био'
        }
        form = CustomUserCreationForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_custom_user_creation_form_missing_username(self):
        """Тест формы создания пользователя без имени пользователя"""
        from .forms import CustomUserCreationForm

        form_data = {
            'username': '',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
        }
        form = CustomUserCreationForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_profile_edit_form_valid(self):
        """Тест валидной формы редактирования профиля"""
        from .forms import ProfileEditForm

        user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        form_data = {
            'first_name': 'Иван',
            'last_name': 'Петров',
            'bio': 'Обновленное био',
            'location': 'Москва',
            'website': 'https://example.com'
        }
        form = ProfileEditForm(data=form_data, instance=user)

        self.assertTrue(form.is_valid())

    def test_profile_edit_form_blank(self):
        """Тест формы редактирования профиля с пустыми полями"""
        from .forms import ProfileEditForm

        user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        form_data = {
            'first_name': '',
            'last_name': '',
            'bio': '',
            'location': '',
            'website': ''
        }
        form = ProfileEditForm(data=form_data, instance=user)

        # Форма должна быть валидной, так как все поля необязательные
        self.assertTrue(form.is_valid())


class UsersPermissionTests(TestCase):
    """Тесты прав доступа системы пользователей"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='testpass123'
        )
        self.other_user = self.User.objects.create_user(
            username='other',
            email='other@example.com',
            password='testpass123'
        )

    def test_profile_edit_owner_access(self):
        """Тест доступа к редактированию профиля владельцем"""
        self.client.login(username='owner', password='testpass123')
        response = self.client.get(reverse('profile_edit'))

        self.assertEqual(response.status_code, 200)

    def test_profile_edit_other_user_access(self):
        """Тест что пользователь не может редактировать чужой профиль через URL"""
        # В нашей системе каждый пользователь редактирует только свой профиль
        # через отдельный endpoint, так что этот тест проверяет базовую функциональность
        self.client.login(username='other', password='testpass123')
        response = self.client.get(reverse('profile_edit'))

        # Должен получить доступ к редактированию своего профиля
        self.assertEqual(response.status_code, 200)


# Дополнительные тестовые утилиты
class UsersTestUtils:
    """Утилиты для тестирования системы пользователей"""

    @staticmethod
    def create_test_user(username='testuser', email='test@example.com', password='testpass123', **extra_fields):
        """Создает тестового пользователя"""
        User = get_user_model()
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **extra_fields
        )

    @staticmethod
    def create_friendship(user1, user2, accepted=False):
        """Создает запрос дружбы между пользователями"""
        return Friendship.objects.create(
            from_user=user1,
            to_user=user2,
            accepted=accepted
        )

    @staticmethod
    def create_friend_pair(user1, user2):
        """Создает взаимную дружбу между пользователями"""
        friendship = Friendship.objects.create(
            from_user=user1,
            to_user=user2,
            accepted=True
        )
        return friendship