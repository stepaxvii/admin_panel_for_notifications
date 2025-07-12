# Makefile для управления проектом

.PHONY: help install dev test clean docker-build docker-up docker-down docker-logs docker-restart migrate migrate-create lint format check

# Переменные
PYTHON = python
PIP = pip
DOCKER = docker
DOCKER_COMPOSE = docker-compose
PYTEST = pytest
RUFF = ruff
MYPY = mypy

help: ## Показать справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости
	$(PIP) install -e .

dev: ## Запустить в режиме разработки
	$(PYTHON) -m app.runners.polling

test: ## Запустить тесты
	$(PYTEST) tests/ -v --no-cov

test-cov: ## Запустить тесты с coverage
	$(PYTEST) tests/ -v

test-fast: ## Запустить тесты быстро (без coverage, параллельно)
	$(PYTEST) tests/ -n auto -v --no-cov

test-debug: ## Запустить тесты с подробным выводом
	$(PYTEST) tests/ -v -s --no-cov

test-file: ## Запустить тесты из конкретного файла (указать FILE="путь")
	$(PYTEST) $(FILE) -v --no-cov

test-method: ## Запустить конкретный тест (указать METHOD="путь")
	$(PYTEST) $(METHOD) -v --no-cov

clean: ## Очистить кэш и временные файлы
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

docker-build: ## Собрать Docker образы
	$(DOCKER_COMPOSE) build

docker-up: ## Запустить все сервисы (с Elasticsearch)
	$(DOCKER_COMPOSE) up -d

docker-up-simple: ## Запустить упрощенные сервисы (без Elasticsearch)
	$(DOCKER_COMPOSE) -f docker-compose.simple.yml up -d

docker-down: ## Остановить все сервисы
	$(DOCKER_COMPOSE) down

docker-down-simple: ## Остановить упрощенные сервисы
	$(DOCKER_COMPOSE) -f docker-compose.simple.yml down

docker-logs: ## Показать логи всех сервисов
	$(DOCKER_COMPOSE) logs -f

docker-logs-simple: ## Показать логи упрощенных сервисов
	$(DOCKER_COMPOSE) -f docker-compose.simple.yml logs -f

docker-restart: ## Перезапустить все сервисы
	$(DOCKER_COMPOSE) restart

docker-restart-simple: ## Перезапустить упрощенные сервисы
	$(DOCKER_COMPOSE) -f docker-compose.simple.yml restart

migrate: ## Применить миграции
	$(DOCKER_COMPOSE) exec admin alembic upgrade head

migrate-simple: ## Применить миграции (упрощенная версия)
	$(DOCKER_COMPOSE) -f docker-compose.simple.yml exec admin alembic upgrade head

migrate-create: ## Создать новую миграцию (указать MESSAGE="описание")
	$(DOCKER_COMPOSE) exec admin alembic revision --autogenerate -m "$(MESSAGE)"

migrate-create-simple: ## Создать новую миграцию (упрощенная версия)
	$(DOCKER_COMPOSE) -f docker-compose.simple.yml exec admin alembic revision --autogenerate -m "$(MESSAGE)"

lint: ## Проверить код линтером
	$(RUFF) check app/

format: ## Отформатировать код
	$(RUFF) format app/

check: ## Проверить типы
	$(MYPY) app/

# Elasticsearch команды
elasticsearch-status: ## Проверить статус Elasticsearch
	curl -X GET "localhost:9200/_cluster/health?pretty"

elasticsearch-indices: ## Показать индексы Elasticsearch
	curl -X GET "localhost:9200/_cat/indices?v"

elasticsearch-logs: ## Показать логи Elasticsearch
	$(DOCKER_COMPOSE) logs -f elasticsearch

kibana-logs: ## Показать логи Kibana
	$(DOCKER_COMPOSE) logs -f kibana

filebeat-logs: ## Показать логи Filebeat
	$(DOCKER_COMPOSE) logs -f filebeat

# Логирование
logs-bot: ## Показать логи бота
	$(DOCKER_COMPOSE) logs -f bot

logs-admin: ## Показать логи админ-панели
	$(DOCKER_COMPOSE) logs -f admin

logs-all: ## Показать логи всех сервисов
	$(DOCKER_COMPOSE) logs -f

logs-simple: ## Показать логи упрощенных сервисов
	$(DOCKER_COMPOSE) -f docker-compose.simple.yml logs -f

# Утилиты
shell: ## Открыть shell в контейнере админ-панели
	$(DOCKER_COMPOSE) exec admin bash

shell-simple: ## Открыть shell в контейнере админ-панели (упрощенная версия)
	$(DOCKER_COMPOSE) -f docker-compose.simple.yml exec admin bash

shell-bot: ## Открыть shell в контейнере бота
	$(DOCKER_COMPOSE) exec bot bash

shell-bot-simple: ## Открыть shell в контейнере бота (упрощенная версия)
	$(DOCKER_COMPOSE) -f docker-compose.simple.yml exec bot bash

shell-postgres: ## Открыть shell в PostgreSQL
	$(DOCKER_COMPOSE) exec postgres psql -U bot_user -d bot_db

shell-redis: ## Открыть shell в Redis
	$(DOCKER_COMPOSE) exec redis redis-cli -a redis_password_here

# Мониторинг
status: ## Показать статус всех сервисов
	$(DOCKER_COMPOSE) ps

status-simple: ## Показать статус упрощенных сервисов
	$(DOCKER_COMPOSE) -f docker-compose.simple.yml ps

health: ## Проверить здоровье сервисов
	@echo "Проверка Elasticsearch..."
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:9200/_cluster/health || echo "недоступен"
	@echo "Проверка Kibana..."
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:5601 || echo "недоступен"
	@echo "Проверка админ-панели..."
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:9000 || echo "недоступен"

health-simple: ## Проверить здоровье упрощенных сервисов
	@echo "Проверка админ-панели..."
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:9000 || echo "недоступен"
	@echo "Проверка PostgreSQL..."
	@docker-compose -f docker-compose.simple.yml exec -T postgres pg_isready -U bot_user || echo "недоступен"
	@echo "Проверка Redis..."
	@docker-compose -f docker-compose.simple.yml exec -T redis redis-cli -a redis_password_here ping || echo "недоступен"

# Полная перезагрузка
full-restart: docker-down docker-up ## Полная перезагрузка всех сервисов
	@echo "Ожидание запуска сервисов..."
	@sleep 10
	@echo "Применение миграций..."
	@$(MAKE) migrate
	@echo "Проверка статуса..."
	@$(MAKE) status

full-restart-simple: docker-down-simple docker-up-simple ## Полная перезагрузка упрощенных сервисов
	@echo "Ожидание запуска сервисов..."
	@sleep 10
	@echo "Применение миграций..."
	@$(MAKE) migrate-simple
	@echo "Проверка статуса..."
	@$(MAKE) status-simple

# Логи файлов
view-logs: ## Просмотр логов из файлов
	@echo "=== Логи админ-панели ==="
	@tail -n 20 logs/admin.log 2>/dev/null || echo "Файл логов не найден"
	@echo ""
	@echo "=== Логи бота ==="
	@tail -n 20 logs/bot.log 2>/dev/null || echo "Файл логов не найден"

clear-logs: ## Очистить файлы логов
	rm -f logs/*.log
	@echo "Логи очищены"
