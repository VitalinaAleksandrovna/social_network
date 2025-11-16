"""
Тесты для приложения Photos
Функционал: Unit tests и integration tests для системы фотографий
"""
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from .models import Photo, Comment


class PhotosModelTests(TestCase):
    """Тесты моделей системы фотографий"""

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

        # Создаем тестовое изображение
        self.test_image = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )

    def test_photo_creation(self):
        """Тест создания фотографии"""
        photo = Photo.objects.create(
            user=self.user,
            image=self.test_image,
            caption='Тестовое описание фотографии'
        )

        self.assertEqual(photo.user, self.user)
        self.assertEqual(photo.caption, 'Тестовое описание фотографии')
        self.assertIsNotNone(photo.image)
        self.assertIsNotNone(photo.created_at)
        self.assertIsNotNone(photo.updated_at)

    def test_photo_str_method(self):
        """Тест строкового представления фотографии"""
        photo = Photo.objects.create(
            user=self.user,
            image=self.test_image
        )

        expected_str = f"Фото {photo.id} от {self.user.username}"
        self.assertEqual(str(photo), expected_str)

    def test_photo_likes_count(self):
        """Тест подсчета лайков фотографии"""
        photo = Photo.objects.create(
            user=self.user,
            image=self.test_image
        )

        # Добавляем лайки
        photo.likes.add(self.user)
        photo.likes.add(self.other_user)

        self.assertEqual(photo.likes_count, 2)
        self.assertEqual(photo.likes.count(), 2)

    def test_photo_comments_count(self):
        """Тест подсчета комментариев фотографии"""
        photo = Photo.objects.create(
            user=self.user,
            image=self.test_image
        )

        # Создаем комментарии
        Comment.objects.create(
            photo=photo,
            user=self.user,
            text='Первый комментарий'
        )
        Comment.objects.create(
            photo=photo,
            user=self.other_user,
            text='Второй комментарий'
        )

        self.assertEqual(photo.comments_count, 2)
        self.assertEqual(photo.comments.count(), 2)

    def test_comment_creation(self):
        """Тест создания комментария"""
        photo = Photo.objects.create(
            user=self.user,
            image=self.test_image
        )

        comment = Comment.objects.create(
            photo=photo,
            user=self.user,
            text='Тестовый комментарий'
        )

        self.assertEqual(comment.photo, photo)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.text, 'Тестовый комментарий')
        self.assertIsNotNone(comment.created_at)

    def test_comment_str_method(self):
        """Тест строкового представления комментария"""
        photo = Photo.objects.create(
            user=self.user,
            image=self.test_image
        )

        comment = Comment.objects.create(
            photo=photo,
            user=self.user,
            text='Тестовый комментарий'
        )

        expected_str = f"Комментарий {self.user.username} к фото {photo.id}"
        self.assertEqual(str(comment), expected_str)

    def test_photo_ordering(self):
        """Тест порядка сортировки фотографий"""
        # Создаем фотографии в разном порядке
        photo1 = Photo.objects.create(
            user=self.user,
            image=self.test_image,
            caption='Первая фотография'
        )
        photo2 = Photo.objects.create(
            user=self.user,
            image=self.test_image,
            caption='Вторая фотография'
        )

        photos = Photo.objects.all()
        self.assertEqual(photos[0], photo2)  # Последняя созданная должна быть первой
        self.assertEqual(photos[1], photo1)

    def test_comment_ordering(self):
        """Тест порядка сортировки комментариев"""
        photo = Photo.objects.create(
            user=self.user,
            image=self.test_image
        )

        # Создаем комментарии в разном порядке
        comment1 = Comment.objects.create(
            photo=photo,
            user=self.user,
            text='Первый комментарий'
        )
        comment2 = Comment.objects.create(
            photo=photo,
            user=self.other_user,
            text='Второй комментарий'
        )

        comments = Comment.objects.all()
        self.assertEqual(comments[0], comment1)  # Старые комментарии должны быть первыми
        self.assertEqual(comments[1], comment2)


class PhotosViewTests(TestCase):
    """Тесты представлений системы фотографий"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.test_image = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )

        self.photo = Photo.objects.create(
            user=self.user,
            image=self.test_image,
            caption='Тестовая фотография'
        )

    def test_photo_list_view(self):
        """Тест просмотра списка фотографий"""
        response = self.client.get(reverse('photo_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'photos/photo_list.html')
        self.assertContains(response, 'Лента фотографий')

    def test_photo_detail_view(self):
        """Тест детального просмотра фотографии"""
        response = self.client.get(reverse('photo_detail', args=[self.photo.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'photos/photo_detail.html')
        self.assertContains(response, 'Тестовая фотография')

    def test_upload_photo_view_authenticated(self):
        """Тест загрузки фотографии аутентифицированным пользователем"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('upload_photo'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'photos/upload_photo.html')
        self.assertContains(response, 'Загрузка фотографии')

    def test_upload_photo_view_unauthenticated(self):
        """Тест загрузки фотографии неаутентифицированным пользователем"""
        response = self.client.get(reverse('upload_photo'))

        # Должен перенаправить на страницу входа
        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/login/', response.url)

    def test_like_photo_authenticated(self):
        """Тест лайка фотографии аутентифицированным пользователем"""
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('photo_detail', args=[self.photo.id]),
            {'like': ''}
        )

        # Должен перенаправить обратно на детали фотографии
        self.assertEqual(response.status_code, 302)

        # Проверяем что лайк добавился
        self.assertTrue(self.photo.likes.filter(id=self.user.id).exists())

    def test_comment_photo_authenticated(self):
        """Тест комментария фотографии аутентифицированным пользователем"""
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('photo_detail', args=[self.photo.id]),
            {'comment': '', 'text': 'Тестовый комментарий'}
        )

        # Должен перенаправить обратно на детали фотографии
        self.assertEqual(response.status_code, 302)

        # Проверяем что комментарий создался
        comment = Comment.objects.filter(text='Тестовый комментарий').first()
        self.assertIsNotNone(comment)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.photo, self.photo)


class PhotosFormTests(TestCase):
    """Тесты форм системы фотографий"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.test_image = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )

    def test_photo_form_valid(self):
        """Тест валидной формы фотографии"""
        from .forms import PhotoForm

        form_data = {
            'caption': 'Тестовое описание фотографии'
        }
        form_files = {
            'image': self.test_image
        }
        form = PhotoForm(data=form_data, files=form_files)

        self.assertTrue(form.is_valid())

    def test_photo_form_no_image(self):
        """Тест формы фотографии без изображения"""
        from .forms import PhotoForm

        form_data = {
            'caption': 'Тестовое описание фотографии'
        }
        form = PhotoForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn('image', form.errors)

    def test_comment_form_valid(self):
        """Тест валидной формы комментария"""
        from .forms import CommentForm

        form_data = {'text': 'Валидный комментарий'}
        form = CommentForm(data=form_data)

        self.assertTrue(form.is_valid())

    def test_comment_form_empty(self):
        """Тест пустой формы комментария"""
        from .forms import CommentForm

        form_data = {'text': ''}
        form = CommentForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn('text', form.errors)

    def test_comment_form_whitespace(self):
        """Тест формы комментария только с пробелами"""
        from .forms import CommentForm

        form_data = {'text': '   '}
        form = CommentForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn('text', form.errors)


class PhotosPermissionTests(TestCase):
    """Тесты прав доступа системы фотографий"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.User = get_user_model()
        self.owner = self.User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='testpass123'
        )
        self.other_user = self.User.objects.create_user(
            username='other',
            email='other@example.com',
            password='testpass123'
        )

        self.test_image = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )

        self.photo = Photo.objects.create(
            user=self.owner,
            image=self.test_image,
            caption='Фотография владельца'
        )

        def tearDown(self):
            """Очистка после тестов"""
            # Удаляем тестовые файлы
            for photo in Photo.objects.all():
                if photo.image:
                    photo.image.delete(save=False)

    def test_photo_delete_owner(self):
        """Тест удаления фотографии владельцем"""
        self.client.force_login(self.owner)

        response = self.client.post(reverse('delete_photo', args=[self.photo.id]))

        # Должен перенаправить на список фотографий
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('photo_list'))

        # Проверяем что фотография удалилась
        with self.assertRaises(Photo.DoesNotExist):
            Photo.objects.get(id=self.photo.id)

    def test_photo_delete_non_owner(self):
        """Тест удаления фотографии не владельцем"""
        self.client.force_login(self.other_user)

        response = self.client.post(reverse('delete_photo', args=[self.photo.id]))

        # Должен вернуть 404, так как фотография не найдена для этого пользователя
        self.assertEqual(response.status_code, 404)


# Дополнительные тестовые утилиты
class PhotosTestUtils:
    """Утилиты для тестирования системы фотографий"""

    @staticmethod
    def create_test_photo(user, caption="Тестовая фотография"):
        """Создает тестовую фотографию"""
        test_image = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )

        return Photo.objects.create(
            user=user,
            image=test_image,
            caption=caption
        )

    @staticmethod
    def create_test_comment(photo, user, text="Тестовый комментарий"):
        """Создает тестовый комментарий"""
        return Comment.objects.create(
            photo=photo,
            user=user,
            text=text
        )

    @staticmethod
    def like_photo(photo, user):
        """Добавляет лайк фотографии"""
        photo.likes.add(user)
        return photo