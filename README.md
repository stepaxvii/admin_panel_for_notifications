# Aiogram Bot Template

Шаблон асинхронного Telegram-бота на базе Aiogram 3.x с FastAPI, Starlette Admin, PostgreSQL, Redis, централизованным логированием и поддержкой локализации.

---

## Основные возможности
- **Telegram-бот** с поддержкой webhook и polling
- **Web API** на FastAPI
- **Админ-панель** на Starlette Admin для управления пользователями и уведомлениями
- **PostgreSQL** (SQLAlchemy + Alembic) для хранения данных
- **Redis** для кэширования и сессий
- **Локализация** (русский, английский) через Fluent (.ftl)
- **Централизованное логирование** (Elasticsearch, Filebeat, Kibana)
- **Контейнеризация** через Docker Compose
- **Модульная архитектура**: Unit of Work, Repository, Dependency Injection, Middleware

---

## Структура проекта

```
aiogram_bot_template/
├── app/                    # Основной код приложения
│   ├── admin/              # Админ-панель: действия, middleware, views
│   ├── const.py            # Константы
│   ├── endpoints/          # FastAPI endpoints (healthcheck, notifications, telegram)
│   ├── enums/              # Перечисления (enums)
│   ├── errors/             # Классы ошибок
│   ├── factory/            # Фабрики: конфиг, сервисы, Redis, Telegram
│   ├── models/             # Модели данных
│   │   ├── sql/            # SQLAlchemy модели (user, notification, миксины)
│   │   ├── dto/            # Pydantic DTO (user, healthcheck)
│   │   ├── state/          # Состояния бота
│   │   └── config/         # Конфиги
│   ├── runners/            # Запуск различных режимов (admin, app, webhook, polling, lifespan)
│   ├── services/           # Бизнес-логика, CRUD, работа с БД и Redis
│   │   ├── crud/           # CRUD-операции
│   │   ├── postgres/       # Репозитории, UoW для Postgres
│   │   └── redis/          # Работа с Redis
│   ├── telegram/           # Telegram-бот: обработчики, фильтры, middleware, клавиатуры
│   │   ├── handlers/       # Хендлеры (main, extra)
│   │   ├── filters/        # Фильтры
│   │   ├── helpers/        # Хелперы
│   │   ├── keyboards/      # Клавиатуры (callback_data, common)
│   │   └── middlewares/    # Middleware для Telegram
│   └── utils/              # Утилиты: локализация, логирование, yaml, время и др.
├── assets/
│   └── messages/           # Локализация сообщений (en, ru, .ftl)
├── docker/                 # Docker и Filebeat конфиги
├── migrations/             # Alembic миграции
├── tests/                  # Тесты (unit, integration, performance)
├── logs/                   # Логи приложения
├── requirements.txt        # Зависимости
├── pyproject.toml          # Метаинформация проекта
├── docker-compose.yml      # Docker Compose
├── Dockerfile              # Dockerfile
├── Makefile                # Makefile
├── README.md               # Описание проекта
```

---

## Краткое описание ключевых модулей

- **admin/** — административные действия, middleware, представления для управления пользователями и уведомлениями.
- **endpoints/** — FastAPI endpoints: healthcheck, уведомления, интеграция с Telegram.
- **factory/** — фабрики для конфигов, сервисов, Redis, Telegram (бот, dispatcher, i18n).
- **models/** — модели данных: SQLAlchemy (sql/), Pydantic DTO (dto/), состояния (state/), конфиги (config/).
- **runners/** — запуск приложения в разных режимах: polling, webhook, lifespan, admin.
- **services/** — бизнес-логика, CRUD, репозитории, Unit of Work, работа с Postgres и Redis.
- **telegram/** — обработчики команд и сообщений, фильтры, middleware, клавиатуры, хелперы для Telegram-бота.
- **utils/** — утилиты: локализация (localization/), логирование (logging/), yaml, время, типы и др.
- **assets/messages/** — локализация сообщений на Fluent (.ftl) для разных языков.

---

## Быстрый старт (Docker Compose)

```bash
git clone <repository-url>
cd aiogram_bot_template
cp .env.example .env  # или создайте .env вручную
# Отредактируйте .env под свои нужды

docker-compose up -d
```

---

## Переменные окружения (пример)

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_USE_WEBHOOK=true
TELEGRAM_WEBHOOK_PATH=/webhook
TELEGRAM_WEBHOOK_SECRET=your_webhook_secret
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
ADMIN_PORT=9000
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=bot_user
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=bot_db
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis_password
ENVIRONMENT=docker
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log
```

---

## Запуск и разработка

- **Инфраструктура (БД, Redis, Elasticsearch, Kibana):**
  ```bash
  docker-compose up -d postgres redis elasticsearch kibana
  ```
- **Бот (polling):**
  ```bash
  python -m app.runners.polling
  ```
- **Бот (webhook):**
  ```bash
  python -m app.runners.webhook
  ```
- **Админ-панель:**
  ```bash
  python -m app.runners.admin
  ```
- **Lifespan (служебные задачи):**
  ```bash
  python -m app.runners.lifespan
  ```

---

## Миграции базы данных

```bash
alembic revision --autogenerate -m "Описание изменений"
alembic upgrade head
alembic downgrade -1
```

---

## Тестирование

```bash
pytest
pytest --cov=app --cov-report=html
pytest -m integration
```

---

## Локализация
- Все сообщения вынесены в assets/messages/en/ и assets/messages/ru/ (формат Fluent .ftl)
- Менеджер локализации: app/utils/localization/
- Локализация поддерживается на уровне Telegram-бота и админ-панели

---

## Логирование и мониторинг
- Структурированное логирование (JSON) через utils/logging/
- Filebeat для сбора логов, Elasticsearch и Kibana для визуализации
- Мониторинг ошибок, производительности, бизнес-метрик

---

## API Endpoints (примеры)

- `POST /api/notifications/send` — массовая отправка уведомлений
- `GET /api/notifications/{notification_id}/status` — статус уведомления
- `GET /api/notifications/recent?limit=10` — последние уведомления
- `POST /api/notifications/retry/{notification_id}` — повторная отправка
- `GET /api/user` — список пользователей (админка)
- `GET /health` — healthcheck

---

## Админ-панель
- Веб-интерфейс для управления пользователями и уведомлениями
- Просмотр, поиск, фильтрация пользователей
- CRUD для уведомлений
- Автоматическое определение и блокировка пользователей, заблокировавших бота
- Предпросмотр уведомлений

---

## Рекомендации для продакшена
- Настроить SSL/TLS
- Использовать внешние БД и Redis
- Настроить бэкапы
- Включить аутентификацию для админ-панели
- Мониторить через Kibana

---

## Устранение неполадок
- Проверяйте логи (docker-compose logs, logs/)
- Проверяйте конфиги Nginx и переменные окружения
- Используйте тестовые команды для диагностики API и БД

---

## Авторы и лицензия

[Укажите авторов и лицензию проекта]
