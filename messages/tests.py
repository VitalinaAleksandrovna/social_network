"""
Тесты для приложения Messages
Функционал: Unit tests и integration tests для системы сообщений
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Conversation, Message


class MessagesModelTests(TestCase):
    """Тесты моделей системы сообщений"""

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

    def test_conversation_creation(self):
        """Тест создания беседы"""
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user1, self.user2)

        self.assertEqual(conversation.participants.count(), 2)
        self.assertTrue(self.user1 in conversation.participants.all())
        self.assertTrue(self.user2 in conversation.participants.all())

    def test_message_creation(self):
        """Тест создания сообщения"""
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user1, self.user2)

        message = Message.objects.create(
            conversation=conversation,
            sender=self.user1,
            content='Тестовое сообщение'
        )

        self.assertEqual(message.conversation, conversation)
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.content, 'Тестовое сообщение')
        self.assertFalse(message.read)

    def test_conversation_str_method(self):
        """Тест строкового представления беседы"""
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user1, self.user2)

        expected_str = f"Беседа: {self.user1.username}, {self.user2.username}"
        self.assertEqual(str(conversation), expected_str)

    def test_message_str_method(self):
        """Тест строкового представления сообщения"""
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user1, self.user2)

        message = Message.objects.create(
            conversation=conversation,
            sender=self.user1,
            content='Тестовое сообщение'
        )

        self.assertIn(self.user1.username, str(message))
        self.assertIn('Сообщение от', str(message))

    def test_conversation_last_message_property(self):
        """Тест свойства last_message беседы"""
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user1, self.user2)

        # Создаем несколько сообщений
        message1 = Message.objects.create(
            conversation=conversation,
            sender=self.user1,
            content='Первое сообщение'
        )
        message2 = Message.objects.create(
            conversation=conversation,
            sender=self.user2,
            content='Второе сообщение'
        )

        self.assertEqual(conversation.last_message, message2)

    def test_conversation_unread_count(self):
        """Тест подсчета непрочитанных сообщений"""
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user1, self.user2)

        # Создаем сообщения
        Message.objects.create(
            conversation=conversation,
            sender=self.user1,
            content='Сообщение 1'
        )
        Message.objects.create(
            conversation=conversation,
            sender=self.user2,
            content='Сообщение 2',
            read=True
        )
        Message.objects.create(
            conversation=conversation,
            sender=self.user1,
            content='Сообщение 3'
        )

        # Для user2 должно быть 2 непрочитанных сообщения
        unread_count = conversation.get_unread_count(self.user2)
        self.assertEqual(unread_count, 2)

        # Для user1 должно быть 0 непрочитанных (он отправитель)
        unread_count_user1 = conversation.get_unread_count(self.user1)
        self.assertEqual(unread_count_user1, 0)

    def test_message_mark_as_read(self):
        """Тест пометки сообщения как прочитанного"""
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user1, self.user2)

        message = Message.objects.create(
            conversation=conversation,
            sender=self.user1,
            content='Тестовое сообщение'
        )

        self.assertFalse(message.read)
        message.mark_as_read()
        self.assertTrue(message.read)


class MessagesViewTests(TestCase):
    """Тесты представлений системы сообщений"""

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

        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)

        self.message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content='Тестовое сообщение'
        )

    def test_inbox_view_authenticated(self):
        """Тест просмотра входящих аутентифицированным пользователем"""
        self.client.force_login(self.user1)
        response = self.client.get(reverse('inbox'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'messages/inbox.html')
        self.assertContains(response, 'Входящие сообщения')

    def test_inbox_view_unauthenticated(self):
        """Тест просмотра входящих неаутентифицированным пользователем"""
        response = self.client.get(reverse('inbox'))

        # Должен перенаправить на страницу входа
        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/login/', response.url)

    def test_conversation_detail_view(self):
        """Тест детального просмотра беседы"""
        self.client.force_login(self.user1)
        response = self.client.get(reverse('conversation_detail', args=[self.conversation.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'messages/conversation_detail.html')
        self.assertContains(response, 'Тестовое сообщение')

    def test_send_message_view(self):
        """Тест отправки сообщения"""
        self.client.force_login(self.user1)

        response = self.client.post(
            reverse('send_message', args=[self.user2.username]),
            {'content': 'Новое тестовое сообщение'}
        )

        # Должен перенаправить на детали беседы
        self.assertEqual(response.status_code, 302)

        # Проверяем что сообщение создалось
        new_message = Message.objects.filter(content='Новое тестовое сообщение').first()
        self.assertIsNotNone(new_message)
        self.assertEqual(new_message.sender, self.user1)

    def test_start_conversation_view_get(self):
        """Тест GET запроса начала новой беседы"""
        self.client.force_login(self.user1)
        response = self.client.get(reverse('start_conversation'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'messages/start_conversation.html')
        self.assertContains(response, 'Новая беседа')

    def test_start_conversation_view_post(self):
        """Тест POST запроса начала новой беседы"""
        self.client.force_login(self.user1)

        response = self.client.post(
            reverse('start_conversation'),
            {
                'recipient_username': self.user2.username,
                'message': 'Первое сообщение в новой беседе'
            }
        )

        # Должен перенаправить на детали беседы
        self.assertEqual(response.status_code, 302)

        # Проверяем что беседа создалась
        new_conversation = Conversation.objects.filter(participants=self.user1).filter(participants=self.user2).first()
        self.assertIsNotNone(new_conversation)

        # Проверяем что сообщение создалось
        new_message = Message.objects.filter(content='Первое сообщение в новой беседе').first()
        self.assertIsNotNone(new_message)


class MessagesFormTests(TestCase):
    """Тесты форм системы сообщений"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.User = get_user_model()
        self.user1 = self.User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )

    def test_message_form_valid(self):
        """Тест валидной формы сообщения"""
        from .forms import MessageForm

        form_data = {'content': 'Валидное сообщение'}
        form = MessageForm(data=form_data)

        self.assertTrue(form.is_valid())

    def test_message_form_empty(self):
        """Тест пустой формы сообщения"""
        from .forms import MessageForm

        form_data = {'content': ''}
        form = MessageForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

    def test_message_form_whitespace(self):
        """Тест формы сообщения только с пробелами"""
        from .forms import MessageForm

        form_data = {'content': '   '}
        form = MessageForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

    def test_new_conversation_form_valid(self):
        """Тест валидной формы новой беседы"""
        from .forms import NewConversationForm

        form_data = {
            'recipient_username': 'user2',
            'message': 'Первое сообщение'
        }
        form = NewConversationForm(data=form_data)

        self.assertTrue(form.is_valid())

    def test_new_conversation_form_missing_recipient(self):
        """Тест формы новой беседы без получателя"""
        from .forms import NewConversationForm

        form_data = {
            'recipient_username': '',
            'message': 'Первое сообщение'
        }
        form = NewConversationForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn('recipient_username', form.errors)


# Дополнительные тестовые утилиты
class MessagesTestUtils:
    """Утилиты для тестирования системы сообщений"""

    @staticmethod
    def create_test_conversation_with_messages(user1, user2, message_count=3):
        """Создает тестовую беседу с сообщениями"""
        conversation = Conversation.objects.create()
        conversation.participants.add(user1, user2)

        messages = []
        for i in range(message_count):
            sender = user1 if i % 2 == 0 else user2
            message = Message.objects.create(
                conversation=conversation,
                sender=sender,
                content=f'Тестовое сообщение {i + 1}'
            )
            messages.append(message)

        return conversation, messages

    @staticmethod
    def get_conversation_between_users(user1, user2):
        """Находит беседу между двумя пользователями"""
        return Conversation.objects.filter(
            participants=user1
        ).filter(
            participants=user2
        ).first()