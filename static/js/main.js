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