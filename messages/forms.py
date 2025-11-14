"""
Формы для системы сообщений
Функционал: Создание и отправка сообщений
"""
from django import forms
from .models import Message


class MessageForm(forms.ModelForm):
    """Форма отправки сообщения"""

    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите сообщение...',
                'rows': 3,
                'maxlength': 2000
            })
        }

    def clean_content(self):
        """Валидация содержания сообщения"""
        content = self.cleaned_data.get('content')
        if len(content.strip()) < 1:
            raise forms.ValidationError("Сообщение не может быть пустым")
        return content


class NewConversationForm(forms.Form):
    """Форма создания новой беседы"""
    recipient_username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите имя пользователя'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Первое сообщение...',
            'rows': 3
        })
    )