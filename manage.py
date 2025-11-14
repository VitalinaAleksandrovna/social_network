#!/usr/bin/env python
"""
Django management script для Social Network проекта.

Функционал: Основной скрипт для управления Django проектом
Команды:
- runserver - запуск сервера разработки
- migrate - применение миграций базы данных
- makemigrations - создание миграций
- createsuperuser - создание администратора
- shell - Django shell для отладки
- test - запуск тестов
"""

import os
import sys


def main():
    """Основная функция управления Django."""

    # Настройка настроек Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_network.settings')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Выполнение команды из командной строки
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()