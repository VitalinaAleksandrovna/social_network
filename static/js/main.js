// Social Network Main JavaScript

class SocialNetwork {
    constructor() {
        this.apiBaseUrl = '/api';
        this.isLoading = false;
        this.init();
    }

    init() {
        this.setupCSRF();
        this.setupAjaxHandlers();
        this.setupUIInteractions();
        this.setupLikeHandlers(); // ПЕРЕНЕСЕНО В НАЧАЛО
        this.fixAvatarSizes();
    }

    // ДОБАВИТЬ НОВЫЙ МЕТОД ДЛЯ ФИКСА РАЗМЕРОВ АВАТАРОК
    fixAvatarSizes() {
        // Принудительно фиксируем размеры всех аватарок
        const fixAllAvatars = () => {
            const avatars = document.querySelectorAll(`
                img[src*="profile_picture"],
                .user-avatar-small,
                .user-avatar,
                .user-avatar-medium,
                .user-avatar-large,
                [class*="avatar-fallback"]
            `);

            avatars.forEach(avatar => {
                // Убираем любые inline стили которые могут переопределять размеры
                avatar.style.width = '';
                avatar.style.height = '';
                avatar.style.maxWidth = '';
                avatar.style.maxHeight = '';
                avatar.style.minWidth = '';
                avatar.style.minHeight = '';

                // Принудительно применяем правильные классы
                if (avatar.classList.contains('user-avatar-small') || avatar.src?.includes('profile_picture')) {
                    avatar.classList.add('user-avatar-small');
                } else if (avatar.classList.contains('user-avatar')) {
                    avatar.classList.add('user-avatar');
                }
            });
        };

        // Запускаем сразу
        setTimeout(fixAllAvatars, 100);

        // Запускаем после полной загрузки страницы
        window.addEventListener('load', fixAllAvatars);

        // Запускаем при изменении DOM (для динамического контента)
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.addedNodes.length) {
                    fixAllAvatars();
                }
            });
        });
        observer.observe(document.body, { childList: true, subtree: true });
    }

    setupCSRF() {
        // CSRF token для всех AJAX запросов
        const csrfToken = this.getCSRFToken();
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrfToken);
                }
            }
        });
    }

    getCSRFToken() {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 10) === 'csrftoken=') {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        return cookieValue;
    }

    setupAjaxHandlers() {
        // Глобальная обработка AJAX ошибок
        const self = this;

        $(document).ajaxError(function(event, jqXHR, ajaxSettings, thrownError) {
            console.error('AJAX Error:', thrownError);

            if (jqXHR.status === 403) {
                self.showNotification('Ошибка доступа', 'danger');
            } else if (jqXHR.status === 401) {
                self.showNotification('Требуется авторизация', 'warning');
                setTimeout(() => {
                    window.location.href = '/users/login/';
                }, 2000);
            } else if (jqXHR.status === 500) {
                self.showNotification('Ошибка сервера', 'danger');
            }
        });
    }

    setupUIInteractions() {
        // Инициализация tooltips
        if (typeof $.fn.tooltip !== 'undefined') {
            $('[data-bs-toggle="tooltip"]').tooltip();
        }

        // Auto-dismiss alerts
        $('.alert').delay(5000).fadeOut(300);

        // Image loading handlers
        this.setupImageHandlers();

        // Infinite scroll (если нужно)
        this.setupInfiniteScroll();
    }

    // ОБНОВЛЕННЫЙ МЕТОД ДЛЯ ОБРАБОТКИ ЛАЙКОВ
    setupLikeHandlers() {
        console.log('Setting up like handlers...');
        
        // Обработчики для лайков в ленте
        document.addEventListener('submit', (e) => {
            const likeForm = e.target.closest('form[action*="/like/"]');
            if (likeForm) {
                e.preventDefault();
                this.handleLike(likeForm);
            }
        });

        // Также добавляем обработчик для кнопок с классом like-form
        document.addEventListener('click', (e) => {
            const likeForm = e.target.closest('.like-form, .like-form-detail');
            if (likeForm && e.target.type === 'submit') {
                e.preventDefault();
                this.handleLike(likeForm);
            }
        });
    }

    // ОБНОВЛЕННЫЙ МЕТОД ДЛЯ ОБРАБОТКИ ЛАЙКОВ
    async handleLike(form) {
        if (this.isLoading) return;

        this.isLoading = true;
        const formData = new FormData(form);
        const url = form.action;
        const button = form.querySelector('button');
        const likeCountElements = form.querySelectorAll('.like-count');
        const likeText = form.querySelector('.like-text');

        // Сохраняем оригинальное состояние
        const originalHTML = button.innerHTML;
        const originalClass = button.className;

        // Показываем состояние загрузки
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        button.disabled = true;

        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('Like response:', data);

            if (data.liked !== undefined) {
                // Обновляем интерфейс
                likeCountElements.forEach(likeCount => {
                    likeCount.textContent = data.likes_count;
                });

                if (data.liked) {
                    button.classList.remove('btn-outline-danger');
                    button.classList.add('btn-danger');
                    if (likeText) likeText.textContent = 'Не нравится';
                    button.innerHTML = '<i class="fas fa-heart"></i> ' + data.likes_count;
                } else {
                    button.classList.remove('btn-danger');
                    button.classList.add('btn-outline-danger');
                    if (likeText) likeText.textContent = 'Нравится';
                    button.innerHTML = '<i class="fas fa-heart"></i> ' + data.likes_count;
                }

                // Обновляем все счетчики лайков на странице с тем же photo_id
                const photoId = url.match(/\/photos\/(\d+)\/like/);
                if (photoId) {
                    document.querySelectorAll(`[data-photo-id="${photoId[1]}"] .like-count`).forEach(el => {
                        el.textContent = data.likes_count;
                    });
                }

                this.showNotification(data.liked ? '❤️ Лайк добавлен' : '💔 Лайк удален', 'success');
            }
        } catch (error) {
            console.error('Like error:', error);
            this.showNotification('Ошибка при обновлении лайка', 'danger');

            // Восстанавливаем оригинальное состояние
            button.innerHTML = originalHTML;
            button.className = originalClass;
            
            // Fallback: отправляем форму обычным способом
            form.submit();
        } finally {
            this.isLoading = false;
            button.disabled = false;
        }
    }

    setupImageHandlers() {
        // Обработка ошибок загрузки изображений
        $('img').on('error', function() {
            const defaultImage = '/static/images/default-image.png';
            if ($(this).attr('src') !== defaultImage) {
                $(this).attr('src', defaultImage);
            }
        });

        // Lazy loading для изображений
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.classList.remove('lazy');
                            imageObserver.unobserve(img);
                        }
                    }
                });
            });

            document.querySelectorAll('img.lazy').forEach(img => {
                imageObserver.observe(img);
            });
        }

        // ФИКС: Предотвращаем применение аватарных стилей к обычным фотографиям
        this.fixPhotoSizes();
    }

    // НОВЫЙ МЕТОД: Фикс размеров фотографий
    fixPhotoSizes() {
        const fixAllPhotos = () => {
            const photos = document.querySelectorAll(`
                .photo-card-image,
                .photo-detail-image,
                .photo-large,
                .photo-upload-preview,
                img[src*="/media/photos/"],
                img[src*="/media/"],
                .card img:not([class*="avatar"]):not(.user-avatar)
            `);

            photos.forEach(photo => {
                // Пропускаем аватарки
                if (photo.classList.contains('user-avatar') || 
                    photo.classList.contains('user-avatar-small') ||
                    photo.src?.includes('profile_picture')) {
                    return;
                }

                // Сбрасываем стили для фотографий
                photo.style.width = '';
                photo.style.height = '';
                photo.style.maxWidth = '';
                photo.style.maxHeight = '';
                photo.style.minWidth = '';
                photo.style.minHeight = '';
                photo.style.borderRadius = '';
                photo.style.objectFit = '';

                // Применяем классы в зависимости от контекста
                if (photo.classList.contains('photo-card-image')) {
                    photo.style.cssText = 'width: 100% !important; height: 400px !important; object-fit: cover !important; border-radius: 8px 8px 0 0 !important;';
                } else if (photo.classList.contains('photo-detail-image') || photo.classList.contains('photo-large')) {
                    photo.style.cssText = 'max-width: 100% !important; max-height: 80vh !important; width: auto !important; height: auto !important; object-fit: contain !important; border-radius: 15px !important;';
                } else if (photo.classList.contains('photo-upload-preview')) {
                    photo.style.cssText = 'max-width: 100% !important; max-height: 70vh !important; width: auto !important; height: auto !important; object-fit: contain !important; border-radius: 8px !important;';
                }
            });
        };

        // Запускаем сразу
        setTimeout(fixAllPhotos, 100);
        window.addEventListener('load', fixAllPhotos);

        // Наблюдатель за изменениями DOM
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.addedNodes.length) {
                    fixAllPhotos();
                }
            });
        });
        observer.observe(document.body, { childList: true, subtree: true });
    }

    setupInfiniteScroll() {
        // Базовая реализация бесконечной прокрутки
        const self = this;

        $(window).on('scroll', function() {
            if (self.isLoading) return;

            if ($(window).scrollTop() + $(window).height() > $(document).height() - 100) {
                self.loadMoreContent();
            }
        });
    }

    async loadMoreContent() {
        if (this.isLoading) return;

        this.isLoading = true;
        try {
            // Реализация загрузки дополнительного контента
            console.log('Loading more content...');
            // Здесь должна быть логика загрузки
        } catch (error) {
            console.error('Error loading more content:', error);
        } finally {
            this.isLoading = false;
        }
    }

    // API методы
    async apiRequest(endpoint, options = {}) {
        const url = `${this.apiBaseUrl}${endpoint}`;
        const config = {
            headers: {
                'X-CSRFToken': this.getCSRFToken(),
                'Content-Type': 'application/json',
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Уведомления
    showNotification(message, type = 'info') {
        const alertClass = {
            'success': 'alert-success',
            'danger': 'alert-danger',
            'warning': 'alert-warning',
            'info': 'alert-info'
        }[type] || 'alert-info';

        const alertHtml = `
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        // Создаем контейнер если его нет
        if ($('.messages').length === 0) {
            $('body').prepend('<div class="messages container mt-3"></div>');
        }

        $('.messages').append(alertHtml);

        // Автоматическое скрытие
        setTimeout(() => {
            $('.alert').alert('close');
        }, 5000);
    }

    // Работа с фотографиями
    async likePhoto(photoId) {
        try {
            const data = await this.apiRequest(`/photos/${photoId}/like/`, {
                method: 'POST'
            });
            return data;
        } catch (error) {
            this.showNotification('Ошибка при обновлении лайка', 'danger');
            throw error;
        }
    }

    // Работа с друзьями
    async sendFriendRequest(username) {
        try {
            const data = await this.apiRequest(`/users/${username}/send_friend_request/`, {
                method: 'POST'
            });
            this.showNotification('Запрос на дружбу отправлен', 'success');
            return data;
        } catch (error) {
            this.showNotification('Ошибка при отправке запроса', 'danger');
            throw error;
        }
    }

    // Валидация форм
    validateForm(formElement) {
        const form = $(formElement);
        let isValid = true;

        form.find('[required]').each(function() {
            if (!$(this).val().trim()) {
                isValid = false;
                $(this).addClass('is-invalid');
            } else {
                $(this).removeClass('is-invalid');
            }
        });

        return isValid;
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    window.socialApp = new SocialNetwork();
});

// Вспомогательные функции
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;

    const minute = 60 * 1000;
    const hour = minute * 60;
    const day = hour * 24;

    if (diff < minute) {
        return 'только что';
    } else if (diff < hour) {
        return `${Math.floor(diff / minute)} мин. назад`;
    } else if (diff < day) {
        return `${Math.floor(diff / hour)} ч. назад`;
    } else {
        return date.toLocaleDateString('ru-RU');
    }
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substr(0, maxLength) + '...';
}

// ДОБАВИТЬ: Глобальная функция для принудительного исправления аватарок
function forceFixAvatarSizes() {
    const avatars = document.querySelectorAll(`
        .user-avatar-small,
        .user-avatar,
        .user-avatar-medium,
        .user-avatar-large,
        [class*="avatar-fallback"]
    `);

    avatars.forEach(avatar => {
        avatar.style.width = '';
        avatar.style.height = '';
        avatar.style.maxWidth = '';
        avatar.style.maxHeight = '';
    });
}

// ДОБАВИТЬ: Функция для исправления размеров фотографий
function forceFixPhotoSizes() {
    const photos = document.querySelectorAll(`
        .photo-card-image,
        .photo-detail-image,
        .photo-large,
        img[src*="/media/photos/"]
    `);

    photos.forEach(photo => {
        // Пропускаем аватарки
        if (photo.classList.contains('user-avatar') || photo.src?.includes('profile_picture')) {
            return;
        }
        
        photo.style.width = '';
        photo.style.height = '';
        photo.style.maxWidth = '';
        photo.style.maxHeight = '';
        photo.style.borderRadius = '';
        photo.style.objectFit = '';
    });
}

// ДОБАВИТЬ: Вызов функций при загрузке
document.addEventListener('DOMContentLoaded', function() {
    forceFixAvatarSizes();
    forceFixPhotoSizes();
});

window.addEventListener('load', function() {
    forceFixAvatarSizes();
    forceFixPhotoSizes();
});