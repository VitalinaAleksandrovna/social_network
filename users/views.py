"""
Представления для управления пользователями
Функционал: Регистрация, вход, профили, управление друзьями
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .forms import CustomUserCreationForm, ProfileEditForm
from .models import CustomUser, Friendship


def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('photo_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """Аутентификация пользователя"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Вы вошли как {username}')
            return redirect('photo_list')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    return render(request, 'users/login.html')


def logout_view(request):
    """Выход пользователя"""
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('login')


@login_required
def user_profile(request, username):
    """Просмотр профиля пользователя"""
    profile_user = get_object_or_404(CustomUser, username=username)

    # Проверяем статус дружбы
    friendship_status = None
    if request.user != profile_user:
        friendship = Friendship.objects.filter(
            from_user=request.user,
            to_user=profile_user
        ).first()
        if friendship:
            friendship_status = 'accepted' if friendship.accepted else 'pending'
        else:
            reverse_friendship = Friendship.objects.filter(
                from_user=profile_user,
                to_user=request.user
            ).first()
            if reverse_friendship:
                friendship_status = 'accepted' if reverse_friendship.accepted else 'request_received'

    context = {
        'profile_user': profile_user,
        'friendship_status': friendship_status,
    }
    return render(request, 'users/profile.html', context)


@login_required
def profile_edit(request):
    """Редактирование профиля текущего пользователя"""
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('user_profile', username=request.user.username)
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'users/profile_edit.html', {'form': form})


@login_required
def send_friend_request(request, username):
    """Отправка запроса на дружбу"""
    if request.method == 'POST':
        to_user = get_object_or_404(CustomUser, username=username)
        if request.user != to_user:
            friendship, created = Friendship.objects.get_or_create(
                from_user=request.user,
                to_user=to_user
            )
            if created:
                messages.success(request, f'Запрос на дружбу отправлен {to_user.username}')
            else:
                messages.info(request, 'Запрос на дружбу уже отправлен')
        return redirect('user_profile', username=username)
    return None


@login_required
def accept_friend_request(request, username):
    """Принятие запроса на дружбу"""
    if request.method == 'POST':
        from_user = get_object_or_404(CustomUser, username=username)
        friendship = get_object_or_404(
            Friendship,
            from_user=from_user,
            to_user=request.user
        )
        friendship.accepted = True
        friendship.save()
        messages.success(request, f'Вы теперь друзья с {from_user.username}')
        return redirect('user_profile', username=username)
    return None