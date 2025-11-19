"""
Представления для работы с фотографиями
Функционал: Лента фотографий, детальный просмотр, лайки, комментарии
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Photo, Comment
from .forms import PhotoForm, CommentForm


def photo_list(request):
    """Лента фотографий с пагинацией"""
    photos_list = Photo.objects.all().select_related('user').prefetch_related('likes', 'comments')

    # Пагинация - 12 фото на страницу
    paginator = Paginator(photos_list, 12)
    page_number = request.GET.get('page')
    photos = paginator.get_page(page_number)

    return render(request, 'photos/photo_list.html', {
        'photos': photos,
        'page_title': 'Лента фотографий'
    })


def photo_detail(request, photo_id):
    """Детальный просмотр фотографии с комментариями"""
    photo = get_object_or_404(
        Photo.objects.select_related('user')
        .prefetch_related('likes', 'comments__user'),
        id=photo_id
    )
    comments = photo.comments.all()
    user_has_liked = request.user.is_authenticated and photo.likes.filter(id=request.user.id).exists()

    # Обработка лайков и комментариев
    if request.method == 'POST' and request.user.is_authenticated:
        if 'like' in request.POST:
            # Переключение лайка
            if user_has_liked:
                photo.likes.remove(request.user)
                liked = False
            else:
                photo.likes.add(request.user)
                liked = True

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'liked': liked,
                    'likes_count': photo.likes.count()
                })
            return redirect('photo_detail', photo_id=photo.id)

        elif 'comment' in request.POST:
            # Добавление комментария
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.photo = photo
                comment.user = request.user
                comment.save()
                messages.success(request, 'Комментарий добавлен')
                return redirect('photo_detail', photo_id=photo.id)

    comment_form = CommentForm()

    return render(request, 'photos/photo_detail.html', {
        'photo': photo,
        'comments': comments,
        'comment_form': comment_form,
        'user_has_liked': user_has_liked
    })


@login_required
def upload_photo(request):
    """Загрузка новой фотографии"""
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.user = request.user
            photo.save()
            messages.success(request, 'Фотография успешно загружена!')
            return redirect('photo_detail', photo_id=photo.id)
    else:
        form = PhotoForm()

    return render(request, 'photos/upload_photo.html', {
        'form': form,
        'page_title': 'Загрузка фотографии'
    })


@login_required
def delete_photo(request, photo_id):
    """Удаление фотографии (только владельцем)"""
    photo = get_object_or_404(Photo, id=photo_id, user=request.user)

    if request.method == 'POST':
        photo.delete()
        messages.success(request, 'Фотография удалена')
        return redirect('photo_list')

    return render(request, 'photos/photo_confirm_delete.html', {
        'photo': photo
    })


@login_required
def like_photo(request, photo_id):
    """API endpoint для лайков (AJAX)"""
    if request.method == 'POST':
        photo = get_object_or_404(Photo, id=photo_id)

        # Проверяем, лайкнул ли уже пользователь
        user_has_liked = photo.likes.filter(id=request.user.id).exists()

        if user_has_liked:
            photo.likes.remove(request.user)
            liked = False
        else:
            photo.likes.add(request.user)
            liked = True

        # ОБНОВЛЯЕМ фото из базы чтобы получить актуальные данные
        photo.refresh_from_db()

        # ВОЗВРАЩАЕМ JSON для AJAX
        return JsonResponse({
            'success': True,
            'liked': liked,
            'likes_count': photo.likes.count(),
            'photo_id': photo_id
        })

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)