"""
Формы для загрузки фотографий и комментариев
Функционал: Валидация загружаемых изображений, текста комментариев
"""
from django import forms
from .models import Photo, Comment


class PhotoForm(forms.ModelForm):
    """Форма загрузки новой фотографии"""

    class Meta:
        model = Photo
        fields = ['image', 'caption']
        widgets = {
            'caption': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Добавьте описание к фотографии...',
                'rows': 3
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

    def clean_image(self):
        """Валидация загружаемого изображения"""
        image = self.cleaned_data.get('image')
        if image:
            # Проверка размера файла (максимум 5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Размер изображения не должен превышать 5MB")

            # Проверка формата
            valid_formats = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if image.content_type not in valid_formats:
                raise forms.ValidationError("Поддерживаются только JPEG, PNG, GIF и WebP форматы")

        return image


class CommentForm(forms.ModelForm):
    """Форма добавления комментария"""

    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Добавьте комментарий...',
                'rows': 2,
                'maxlength': 1000
            })
        }

    def clean_text(self):
        """Валидация текста комментария"""
        text = self.cleaned_data.get('text')
        if len(text.strip()) < 1:
            raise forms.ValidationError("Комментарий не может быть пустым")
        return text