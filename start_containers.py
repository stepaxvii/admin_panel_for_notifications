#!/usr/bin/env python3
"""
Простой скрипт для запуска контейнеров.
"""

import subprocess
import time
import os

def main():
    print("=== Запуск контейнеров ===")
    
    # Устанавливаем переменные окружения
    os.environ.update({
        'POSTGRES_HOST': 'postgres',
        'POSTGRES_PORT': '5432',
        'POSTGRES_USER': 'stepa',
        'POSTGRES_PASSWORD': 'stepaxvii',
        'POSTGRES_DB': 'postgres',
        'REDIS_HOST': 'redis',
        'REDIS_PORT': '6379',
        'REDIS_PASSWORD': 'redis_password_here',
        'SERVER_PORT': '8000',
        'ADMIN_PORT': '9000',
        'TELEGRAM_BOT_TOKEN': '',
        'TELEGRAM_WEBHOOK_URL': 'https://your-domain.com/webhook',
        'LOG_LEVEL': 'INFO'
    })
    
    print("Переменные окружения установлены")
    
    # Команды для выполнения
    commands = [
        ("docker-compose down", "Остановка контейнеров"),
        ("docker-compose up -d", "Запуск контейнеров"),
        ("sleep 15", "Ожидание запуска"),
        ("docker-compose ps", "Проверка статуса")
    ]
    
    for cmd, desc in commands:
        print(f"\n{desc}:")
        print(f"Команда: {cmd}")
        
        try:
            if cmd == "sleep 15":
                time.sleep(15)
                print("✅ Ожидание завершено")
            else:
                result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
                print(f"✅ Успешно: {result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка: {e.stderr}")
    
    print("\n=== Контейнеры запущены ===")
    print("Теперь можно запускать: python fix_migrations_final.py")

if __name__ == "__main__":
    main() 