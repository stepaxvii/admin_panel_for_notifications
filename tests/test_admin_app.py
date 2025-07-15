"""
Тестовая версия админ панели для тестов.
"""

import os
from unittest.mock import MagicMock
from fastapi import FastAPI, Request, HTTPException
from fastapi.testclient import TestClient

# Устанавливаем тестовые переменные окружения
os.environ.update({
    "TELEGRAM_BOT_TOKEN": "test_token",
    "POSTGRES_HOST": "localhost",
    "POSTGRES_PORT": "5434",
    "POSTGRES_USER": "test_user",
    "POSTGRES_PASSWORD": "test_password",
    "POSTGRES_DB": "test_db",
    "REDIS_HOST": "localhost",
    "REDIS_PORT": "6380",
    "REDIS_PASSWORD": "test_redis_password",
    "SERVER_HOST": "0.0.0.0",
    "SERVER_PORT": "8081",
    "ADMIN_PORT": "9001",
})

# Создаем тестовое FastAPI приложение
test_app = FastAPI(title="Test Admin Panel")

# Мокаем состояние приложения
test_app.state.bot = MagicMock()
test_app.state.dispatcher = MagicMock()
test_app.state.session_pool = MagicMock()

# Тестовые эндпоинты
@test_app.get("/")
async def admin_home():
    """Главная страница админ панели."""
    return {"message": "Admin Panel Home"}

@test_app.get("/healthcheck")
async def health_check():
    """Проверка состояния."""
    return {"status": "ok"}

@test_app.get("/admin/notification/list")
async def notifications_list():
    """Список уведомлений."""
    return {"notifications": []}

@test_app.get("/admin/user/list")
async def users_list():
    """Список пользователей."""
    return {"users": []}

@test_app.get("/admin/notification/create")
async def create_notification_form():
    """Форма создания уведомления."""
    return {"form": "create_notification"}

@test_app.post("/admin/notification/create")
async def create_notification(request: Request):
    """Создание уведомления."""
    form_data = await request.form()
    text = form_data.get("text", "")
    comment = form_data.get("comment", "")
    
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    return {"message": "Notification created", "text": text, "comment": comment}

@test_app.post("/admin/notification/action")
async def notification_action(request: Request):
    """Действие с уведомлением."""
    form_data = await request.form()
    action = form_data.get("action", "")
    rowid = form_data.get("rowid", "")
    
    if action == "send_notification":
        if not rowid:
            raise HTTPException(status_code=400, detail="Row ID is required")
        return {"message": f"Notification {rowid} sent"}
    
    raise HTTPException(status_code=400, detail="Invalid action")

@test_app.get("/admin/notification/detail/{notification_id}")
async def notification_detail(notification_id: int):
    """Детальная страница уведомления."""
    return {"notification_id": notification_id, "text": "Test notification"}

@test_app.get("/admin/user/detail/{user_id}")
async def user_detail(user_id: int):
    """Детальная страница пользователя."""
    return {"user_id": user_id, "username": "test_user"}

@test_app.post("/admin/notification/edit/{notification_id}")
async def edit_notification(notification_id: int, request: Request):
    """Редактирование уведомления."""
    form_data = await request.form()
    text = form_data.get("text", "")
    comment = form_data.get("comment", "")
    
    return {"message": "Notification updated", "id": notification_id, "text": text, "comment": comment}

@test_app.post("/admin/notification/delete/{notification_id}")
async def delete_notification(notification_id: int):
    """Удаление уведомления."""
    return {"message": "Notification deleted", "id": notification_id}

# API эндпоинты
@test_app.get("/api/notifications")
async def api_notifications_list():
    """API список уведомлений."""
    return []

@test_app.get("/api/notifications/{notification_id}")
async def api_notification_detail(notification_id: int):
    """API детальная информация уведомления."""
    return {"id": notification_id, "text": "Test notification"}

@test_app.post("/api/notifications/send")
async def api_send_notification(request: Request):
    """API отправка уведомления."""
    data = await request.json()
    text = data.get("text", "")
    comment = data.get("comment", "")
    user_ids = data.get("user_ids", [])
    
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    return {
        "message": "Notification sent",
        "sent": len(user_ids),
        "errors": []
    }

@test_app.get("/api/users")
async def api_users_list():
    """API список пользователей."""
    return []

@test_app.get("/api/users/{user_id}")
async def api_user_detail(user_id: int):
    """API детальная информация пользователя."""
    return {"id": user_id, "username": "test_user"}

# Создаем тестовый клиент
test_client = TestClient(test_app) 