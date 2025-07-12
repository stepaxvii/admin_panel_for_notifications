# Telegram Bot Template

Шаблон Telegram бота на Aiogram 3.x с FastAPI, Starlette Admin, PostgreSQL, Redis и Elasticsearch для централизованного логирования.

## Технические характеристики

### Основные компоненты
- **Telegram Bot**: Aiogram 3.7.0+ с поддержкой webhook и polling
- **Web Framework**: FastAPI 0.115.12+ с асинхронной архитектурой
- **Database**: PostgreSQL 16 с SQLAlchemy 2.0.29+ и Alembic для миграций
- **Caching**: Redis 7+ для кэширования и управления сессиями
- **Admin Panel**: Starlette Admin 0.15.1+ для управления уведомлениями
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

### Админ-панель
- Веб-интерфейс для создания уведомлений
- Просмотр статистики и статусов
- Управление пользователями бота
- CRUD операции с уведомлениями
- Предпросмотр уведомлений перед отправкой

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

cp docker-compose.example.yml docker-compose.yml
cp .env.example .env

# Настройка переменных окружения
# Отредактируйте .env файл

docker-compose up -d
```

### Переменные окружения
```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_WEBHOOK_URL=https://your-domain.com/webhook

# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=bot_user
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=bot_db

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis_password

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
ADMIN_PORT=9000

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
│   ├── services/         # Бизнес-логика и сервисы
│   ├── telegram/         # Telegram бот (Aiogram)
│   ├── factory/          # Фабрики для создания компонентов
│   ├── runners/          # Запуск приложений
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

### Health Check
```http
GET /health
```

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
```

## Продакшен развертывание

### Рекомендации по безопасности
- Настройка SSL/TLS для всех сервисов
- Использование внешних PostgreSQL и Redis
- Настройка бэкапов Elasticsearch
- Мониторинг через Kibana алерты
- Логирование в отдельный Elasticsearch кластер

### Масштабирование
```bash
# Горизонтальное масштабирование ботов
docker-compose up -d --scale bot=3

# Отдельный Elasticsearch кластер
# Настройте внешний Elasticsearch в docker-compose.override.yml
```

### Мониторинг производительности
- Отслеживание времени ответа API
- Мониторинг использования памяти и CPU
- Алерты на критические ошибки
- Дашборды для бизнес-метрик
