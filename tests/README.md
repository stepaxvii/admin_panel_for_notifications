# Тесты для админ панели

Этот каталог содержит тесты для админ панели aiogram_bot_template.

## Структура тестов

- `conftest.py` - Конфигурация pytest и фикстуры
- `test_admin_panel.py` - Основные тесты админ панели
- `test_admin_api.py` - Тесты API эндпоинтов
- `test_admin_performance.py` - Тесты производительности
- `test_admin_integration.py` - Интеграционные тесты

## Запуск тестов

### Запуск всех тестов
```bash
pytest tests/
```

### Запуск конкретного файла тестов
```bash
pytest tests/test_admin_panel.py
```

### Запуск с подробным выводом
```bash
pytest tests/ -v
```

### Запуск с покрытием кода
```bash
pytest tests/ --cov=app --cov-report=html
```

### Запуск только быстрых тестов
```bash
pytest tests/ -m "not slow"
```

## Типы тестов

### 1. Основные тесты админ панели (`test_admin_panel.py`)
- Тестирование доступности страниц
- Тестирование создания уведомлений
- Тестирование отправки уведомлений
- Тестирование валидации данных
- Тестирование поиска и пагинации

### 2. API тесты (`test_admin_api.py`)
- Тестирование REST API эндпоинтов
- Тестирование отправки уведомлений через API
- Тестирование получения статистики
- Тестирование обработки ошибок

### 3. Тесты производительности (`test_admin_performance.py`)
- Тестирование времени отклика
- Тестирование одновременных запросов
- Тестирование с большими объемами данных
- Тестирование граничных случаев

### 4. Интеграционные тесты (`test_admin_integration.py`)
- Тестирование полных рабочих процессов
- Тестирование согласованности данных
- Тестирование взаимодействия компонентов
- Тестирование навигации по системе

## Фикстуры

### `client`
Тестовый клиент FastAPI для отправки HTTP запросов.

### `test_config`
Конфигурация приложения для тестов.

### `mock_session_pool`
Мок пула сессий базы данных.

### `mock_redis_repository`
Мок Redis репозитория.

## Примеры использования

### Тестирование создания уведомления
```python
def test_create_notification(self, client: TestClient):
    notification_data = {
        "text": "Test notification",
        "comment": "Test comment"
    }
    
    response = client.post("/admin/notification/create", data=notification_data)
    assert response.status_code in [200, 302]
```

### Тестирование API эндпоинта
```python
def test_send_notification_api(self, client: TestClient):
    notification_data = {
        "text": "API test notification",
        "comment": "API test",
        "user_ids": [123456789]
    }
    
    response = client.post("/api/notifications/send", json=notification_data)
    assert response.status_code in [200, 201]
```

### Тестирование производительности
```python
def test_response_time(self, client: TestClient):
    start_time = time.time()
    response = client.get("/")
    end_time = time.time()
    
    response_time = end_time - start_time
    assert response.status_code == 200
    assert response_time < 1.0
```

## Требования

Для запуска тестов необходимо установить зависимости:
```bash
pip install pytest pytest-asyncio httpx
```

## Настройка окружения

Тесты используют тестовую конфигурацию из `conftest.py`. Убедитесь, что тестовые базы данных доступны или используйте моки.

## Отчеты о покрытии

Для генерации отчета о покрытии кода:
```bash
pytest tests/ --cov=app --cov-report=html --cov-report=term
```

Отчет будет сохранен в `htmlcov/index.html`. 