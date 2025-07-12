"""
Тесты для API эндпоинтов админ панели.
"""

import pytest
from fastapi.testclient import TestClient

from tests.test_admin_app import test_app


class TestAdminAPI:
    """Тесты для API эндпоинтов админ панели."""
    
    @pytest.fixture
    def client(self) -> TestClient:
        """Тестовый клиент для API."""
        return TestClient(test_app)
    
    def test_healthcheck_endpoint(self, client: TestClient):
        """Тест эндпоинта проверки здоровья."""
        response = client.get("/healthcheck")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"
    
    def test_send_notification_endpoint(self, client: TestClient):
        """Тест эндпоинта отправки уведомления."""
        notification_data = {
            "text": "Test notification via API",
            "comment": "Test comment",
            "user_ids": [123456789, 987654321]
        }
        
        response = client.post("/api/notifications/send", json=notification_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "sent" in data
        assert "errors" in data
        assert data["sent"] == 2
    
    def test_invalid_notification_data(self, client: TestClient):
        """Тест отправки некорректных данных уведомления."""
        invalid_data = {
            "text": "",  # Пустой текст
            "comment": "Test comment"
        }
        
        response = client.post("/api/notifications/send", json=invalid_data)
        assert response.status_code == 400
        assert "detail" in response.json()
    
    def test_notification_without_user_ids(self, client: TestClient):
        """Тест отправки уведомления без указания пользователей."""
        notification_data = {
            "text": "Test notification without user IDs",
            "comment": "Test comment"
        }
        
        response = client.post("/api/notifications/send", json=notification_data)
        assert response.status_code == 200
        data = response.json()
        assert data["sent"] == 0
    
    def test_notification_with_empty_user_ids(self, client: TestClient):
        """Тест отправки уведомления с пустым списком пользователей."""
        notification_data = {
            "text": "Test notification with empty user IDs",
            "comment": "Test comment",
            "user_ids": []
        }
        
        response = client.post("/api/notifications/send", json=notification_data)
        assert response.status_code == 200
        data = response.json()
        assert data["sent"] == 0
    
    def test_notification_missing_text(self, client: TestClient):
        """Тест отправки уведомления без текста."""
        notification_data = {
            "comment": "Test comment",
            "user_ids": [123456789]
        }
        
        response = client.post("/api/notifications/send", json=notification_data)
        assert response.status_code == 400
        assert "detail" in response.json()
    
    def test_notification_missing_comment(self, client: TestClient):
        """Тест отправки уведомления без комментария."""
        notification_data = {
            "text": "Test notification without comment",
            "user_ids": [123456789]
        }
        
        response = client.post("/api/notifications/send", json=notification_data)
        assert response.status_code == 200
        data = response.json()
        assert data["sent"] == 1
    
    def test_notification_with_special_characters(self, client: TestClient):
        """Тест отправки уведомления со специальными символами."""
        notification_data = {
            "text": "Test notification with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?",
            "comment": "Test comment with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?",
            "user_ids": [123456789]
        }
        
        response = client.post("/api/notifications/send", json=notification_data)
        assert response.status_code == 200
        data = response.json()
        assert data["sent"] == 1
    
    def test_notification_with_unicode(self, client: TestClient):
        """Тест отправки уведомления с Unicode символами."""
        notification_data = {
            "text": "Тестовое уведомление с русскими символами: привет мир! 🌍",
            "comment": "Комментарий с эмодзи: 🚀",
            "user_ids": [123456789]
        }
        
        response = client.post("/api/notifications/send", json=notification_data)
        assert response.status_code == 200
        data = response.json()
        assert data["sent"] == 1
    
    def test_get_notifications_list_endpoint(self, client: TestClient):
        """Тест эндпоинта получения списка уведомлений."""
        response = client.get("/api/notifications")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_notification_by_id(self, client: TestClient):
        """Тест эндпоинта получения уведомления по ID."""
        response = client.get("/api/notifications/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert "text" in data
    
    def test_get_users_list_endpoint(self, client: TestClient):
        """Тест эндпоинта получения списка пользователей."""
        response = client.get("/api/users")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_user_by_id(self, client: TestClient):
        """Тест эндпоинта получения пользователя по ID."""
        response = client.get("/api/users/123456789")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 123456789
        assert "username" in data
    
    def test_invalid_endpoint(self, client: TestClient):
        """Тест несуществующего эндпоинта."""
        response = client.get("/api/invalid/endpoint")
        assert response.status_code == 404
    
    def test_invalid_method(self, client: TestClient):
        """Тест неверного HTTP метода."""
        response = client.put("/api/notifications/send")
        assert response.status_code == 405  # Method Not Allowed 