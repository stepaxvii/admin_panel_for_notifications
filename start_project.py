#!/usr/bin/env python3
"""
Скрипт для запуска проекта с правильными настройками.
"""

import os
import subprocess
import time
import sys

def set_environment():
    """Установка переменных окружения."""
    env_vars = {
        'POSTGRES_HOST': 'postgres',
        'POSTGRES_PORT': '5432',
        'POSTGRES_USER': 'stepa',
        'POSTGRES_PASSWORD': 'stepaxvii',
        'POSTGRES_DB': 'postgres',
        'POSTGRES_DATA': '/var/lib/postgresql/data',
        'REDIS_HOST': 'redis',
        'REDIS_PORT': '6379',
        'REDIS_PASSWORD': 'redis_password_here',
        'REDIS_DATA': '/data',
        'SERVER_PORT': '8000',
        'ADMIN_PORT': '9000',
        'TELEGRAM_BOT_TOKEN': '7622633582:AAFZwE9GfzhONup4jlNNTMkzrkvYAvaoHNM',
        'TELEGRAM_WEBHOOK_URL': 'https://your-domain.com/webhook',
        'LOG_LEVEL': 'INFO'
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
    
    print("Переменные окружения установлены")

def run_command(cmd, description):
    """Выполнение команды с обработкой ошибок."""
    print(f"\n{description}:")
    print(f"Команда: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Успешно: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"❌ Команда не найдена: {cmd[0]}")
        return False

def main():
    """Основная функция."""
    print("=== Запуск проекта ===")
    
    # Устанавливаем переменные окружения
    set_environment()
    
    # Останавливаем контейнеры
    if not run_command(["docker-compose", "down", "-v"], "Остановка контейнеров"):
        print("Продолжаем...")
    
    # Собираем образы
    if not run_command(["docker-compose", "build"], "Сборка образов"):
        print("Продолжаем...")
    
    # Запускаем контейнеры
    if not run_command(["docker-compose", "up", "-d"], "Запуск контейнеров"):
        print("❌ Не удалось запустить контейнеры")
        sys.exit(1)
    
    # Ждем запуска PostgreSQL
    print("\n⏳ Ожидание запуска PostgreSQL...")
    time.sleep(15)
    
    # Проверяем статус
    if not run_command(["docker-compose", "ps"], "Проверка статуса контейнеров"):
        print("❌ Не удалось проверить статус")
        sys.exit(1)
    
    # Сбрасываем миграции
    print("\n🔄 Сброс миграций...")
    migration_commands = [
        (["docker-compose", "exec", "-T", "postgres", "psql", "-U", "stepa", "-d", "postgres", "-c", "DROP TABLE IF EXISTS alembic_version;"], "Удаление таблицы alembic_version"),
        (["docker-compose", "exec", "-T", "postgres", "psql", "-U", "stepa", "-d", "postgres", "-c", "CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL);"], "Создание таблицы alembic_version"),
        (["docker-compose", "exec", "-T", "postgres", "psql", "-U", "stepa", "-d", "postgres", "-c", "INSERT INTO alembic_version (version_num) VALUES ('002');"], "Установка ревизии 002"),
    ]
    
    for cmd, desc in migration_commands:
        if not run_command(cmd, desc):
            print(f"❌ Ошибка при {desc}")
            continue
    
    # Применяем миграции
    if not run_command(["docker-compose", "exec", "admin", "alembic", "upgrade", "head"], "Применение миграций"):
        print("❌ Ошибка при применении миграций")
        sys.exit(1)
    
    # Проверяем результат
    print("\n🔍 Проверка результата:")
    run_command(["docker-compose", "exec", "postgres", "psql", "-U", "stepa", "-d", "postgres", "-c", "\\dt"], "Список таблиц")
    run_command(["docker-compose", "exec", "postgres", "psql", "-U", "stepa", "-d", "postgres", "-c", "SELECT * FROM alembic_version;"], "Текущая ревизия")
    
    print("\n✅ Проект успешно запущен!")
    print("📊 Логи: docker-compose logs -f")
    print("🌐 Админ-панель: http://localhost:9000")

if __name__ == "__main__":
    main() 