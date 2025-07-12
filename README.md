# Telegram Bot Template

Шаблон Telegram бота на Aiogram 3.x с FastAPI, Starlette Admin, PostgreSQL, Redis и Elasticsearch для централизованного логирования.

## Технические характеристики

### Основные компоненты
- **Telegram Bot**: Aiogram 3.7.0+ с поддержкой webhook и polling
- **Web Framework**: FastAPI 0.115.12+ с асинхронной архитектурой
- **Database**: PostgreSQL 16 с SQLAlchemy 2.0.29+ и Alembic для миграций
- **Caching**: Redis 7+ для кэширования и управления сессиями
- **Admin Panel**: Starlette Admin 0.15.1+ для управления уведомлениями и пользователями
- **Logging**: Централизованное логирование с Elasticsearch 8.11.0 и Kibana
- **Containerization**: Docker Compose для полной контейнеризации

### Архитектурные особенности
- Асинхронная архитектура на основе asyncio
- Unit of Work паттерн для работы с базой данных
- Repository паттерн для абстракции доступа к данным
- Dependency Injection для конфигурации сервисов
- Middleware для обработки событий и пользователей
- Многоязычная поддержка через aiogram-i18n

## Функциональные возможности

### Telegram Bot
- Обработка команд и сообщений
- Система состояний для диалогов
- Многоязычная поддержка (русский, английский)
- Обработка ошибок и исключений
- Middleware для типизации событий

### Система уведомлений
- Массовая отправка уведомлений пользователям
- Отслеживание статуса доставки
- Повторная отправка неудачных уведомлений
- Статистика отправки и ошибок
- API для управления уведомлениями
- **Автоматическая блокировка пользователей**, которые заблокировали бота

### Админ-панель
- Веб-интерфейс для создания уведомлений
- **Просмотр списка пользователей бота**
- **Отображение статуса пользователей (активные/заблокированные)**
- **Поиск пользователей по имени, языку и статусу**
- CRUD операции с уведомлениями
- Предпросмотр уведомлений перед отправкой
- **Автоматическое определение заблокированных пользователей**

### Мониторинг и логирование
- Структурированное JSON логирование
- Централизованный сбор логов через Filebeat
- Визуализация в Kibana
- Мониторинг производительности API
- Отслеживание ошибок и исключений

## Технические требования

### Системные требования
- Python 3.12+
- Docker 20.10+
- Docker Compose 2.0+
- Минимум 2GB RAM для полного стека
- 10GB свободного места на диске

### Зависимости
- aiogram>=3.7.0
- fastapi>=0.115.12
- sqlalchemy>=2.0.29
- asyncpg>=0.30.0
- redis>=5.2.1
- starlette-admin>=0.15.1
- elasticsearch>=8.13.0

## Установка и развертывание

### Быстрый старт с Docker Compose
```bash
git clone <repository-url>
cd aiogram_bot_template

# Создание .env файла с настройками для вашего домена
cat > .env << EOF
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_USE_WEBHOOK=true
TELEGRAM_WEBHOOK_PATH=/webhook
TELEGRAM_WEBHOOK_SECRET=your_webhook_secret_here
TELEGRAM_DROP_PENDING_UPDATES=true
TELEGRAM_RESET_WEBHOOK=false

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SERVER_URL=https://your-domain.com

# Admin Panel Configuration
ADMIN_PORT=9000

# Database Configuration
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=bot_user
POSTGRES_PASSWORD=secure_password_here
POSTGRES_DB=bot_db
POSTGRES_DATA=/var/lib/postgresql/data

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis_password_here
REDIS_DATA=/data

# Environment
ENVIRONMENT=docker

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log
EOF

# Настройка переменных окружения
# Отредактируйте .env файл, заменив:
# - your_bot_token_here на ваш токен бота
# - your_webhook_secret_here на секретный ключ для webhook
# - secure_password_here на безопасный пароль для БД
# - redis_password_here на пароль для Redis

docker-compose up -d
```

### Настройка Nginx для админ-панели
Для корректной работы админ-панели необходимо настроить Nginx для проксирования API запросов:

```nginx
# Основной сервер
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL конфигурация
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Telegram Bot API
    location /api {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
    }

    # Admin Panel API (должен быть перед общим /api)
    location ~ ^/api/(user|notification) {
        proxy_pass http://localhost:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
    }

    # Admin Panel (все остальные запросы)
    location / {
        proxy_pass http://localhost:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
    }
}
```

### Переменные окружения
```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_USE_WEBHOOK=true
TELEGRAM_WEBHOOK_PATH=/webhook
TELEGRAM_WEBHOOK_SECRET=your_webhook_secret_here
TELEGRAM_DROP_PENDING_UPDATES=true
TELEGRAM_RESET_WEBHOOK=false

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SERVER_URL=https://your-domain.com

# Admin Panel Configuration
ADMIN_PORT=9000

# Database Configuration
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=bot_user
POSTGRES_PASSWORD=secure_password_here
POSTGRES_DB=bot_db
POSTGRES_DATA=/var/lib/postgresql/data

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis_password_here
REDIS_DATA=/data

# Environment
ENVIRONMENT=docker

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log
```

## Структура проекта

```
aiogram_bot_template/
├── app/                    # Основной код приложения
│   ├── endpoints/         # API endpoints (FastAPI)
│   ├── models/           # Модели данных (SQLAlchemy, Pydantic)
│   │   ├── sql/         # SQLAlchemy модели
│   │   │   ├── user.py  # Модель пользователя
│   │   │   └── notification.py # Модель уведомлений
│   │   └── dto/         # Pydantic DTO модели
│   ├── services/         # Бизнес-логика и сервисы
│   ├── telegram/         # Telegram бот (Aiogram)
│   ├── factory/          # Фабрики для создания компонентов
│   ├── runners/          # Запуск приложений
│   │   ├── admin.py     # Админ-панель
│   │   └── app.py       # Основное приложение
│   └── utils/            # Утилиты и хелперы
├── migrations/           # Alembic миграции
├── assets/              # Локализация и статические файлы
├── docker/              # Docker конфигурации
├── tests/               # Тесты (pytest)
└── logs/                # Логи приложения
```

## API Endpoints

### Уведомления
```http
POST /api/notifications/send
Content-Type: application/json

{
  "notification_id": 123
}
```

```http
GET /api/notifications/{notification_id}/status
```

```http
GET /api/notifications/recent?limit=10
```

```http
POST /api/notifications/retry/{notification_id}
```

### Админ-панель API
```http
GET /api/user
GET /api/notification
```

### Health Check
```http
GET /health
```

## Админ-панель

### Функции админ-панели
- **Управление уведомлениями**:
  - Создание новых уведомлений
  - Просмотр списка уведомлений
  - Отправка уведомлений всем пользователям
  - Предпросмотр уведомлений
  - Отслеживание статуса отправки

- **Управление пользователями**:
  - Просмотр списка всех пользователей бота
  - Отображение статуса пользователей (активные/заблокированные)
  - Поиск пользователей по имени, языку и статусу
  - Автоматическое определение заблокированных пользователей

### Автоматическая блокировка пользователей
При отправке уведомлений система автоматически:
- Определяет пользователей, которые заблокировали бота
- Обновляет их статус на "blocked" в базе данных
- Исключает их из будущих рассылок
- Логирует информацию о заблокированных пользователях

### Доступ к админ-панели
- URL: `https://your-domain.com/`
- Порт: 9000 (внутренний)
- Аутентификация: отключена (для продакшена рекомендуется настроить)

## Разработка

### Локальная разработка
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

pip install -e .

# Запуск только инфраструктуры
docker-compose up -d postgres redis elasticsearch kibana

# Запуск бота локально
python -m app.runners.polling

# Запуск админ-панели локально
python -m app.runners.admin
```

### Миграции базы данных
```bash
# Создание миграции
alembic revision --autogenerate -m "Описание изменений"

# Применение миграций
alembic upgrade head

# Откат миграции
alembic downgrade -1
```

### Тестирование
```bash
# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=app --cov-report=html

# Запуск интеграционных тестов
pytest -m integration
```

## Мониторинг

### Elasticsearch и Kibana
- Elasticsearch: http://localhost:9200
- Kibana: http://localhost:5601
- Filebeat: Автоматический сбор логов

### Полезные запросы Kibana
```json
// Логи бота
logger: "app.telegram"

// Ошибки
level: "ERROR"

// Медленные запросы
message: "slow_query"

// Уведомления
message: "notification_sent"

// Заблокированные пользователи
message: "заблокирован"
```

## Продакшен развертывание

### Рекомендации по безопасности
- Настройка SSL/TLS для всех сервисов
- Использование внешних PostgreSQL и Redis
- Настройка бэкапов Elasticsearch
- Мониторинг через Kibana алерты
- Логирование в отдельный Elasticsearch кластер
- **Настройка аутентификации для админ-панели**

### Масштабирование
```bash
# Горизонтальное масштабирование ботов
docker-compose up -d --scale bot=3
```

### Мониторинг производительности
- Отслеживание времени ответа API
- Мониторинг использования памяти и CPU
- Алерты на критические ошибки
- Дашборды для бизнес-метрик
- **Мониторинг количества заблокированных пользователей**

## Устранение неполадок

### Проблемы с админ-панелью
1. **Данные не загружаются**: Проверьте конфигурацию Nginx для `/api/user` и `/api/notification`
2. **Ошибки 404**: Убедитесь, что API endpoints проксируются на порт 9000
3. **Проблемы с подключением к БД**: Проверьте переменные окружения POSTGRES_*

### Проблемы с уведомлениями
1. **Пользователи не получают уведомления**: Проверьте логи на наличие заблокированных пользователей
2. **Ошибки отправки**: Проверьте токен бота и права доступа

### Полезные команды для диагностики
```bash
# Проверка статуса контейнеров
docker-compose ps

# Просмотр логов админки
docker-compose logs admin

# Проверка подключения к БД
docker-compose exec admin python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select
from app.models.sql.user import User

async def test_db():
    engine = create_async_engine('postgresql+asyncpg://user:pass@postgres:5432/db')
    async with engine.begin() as conn:
        result = await conn.execute(select(User))
        users = result.fetchall()
        print(f'Found {len(users)} users')
    await engine.dispose()

asyncio.run(test_db())
"

# Проверка API endpoints
curl "https://your-domain.com/api/user"
curl "https://your-domain.com/api/notification"
```
