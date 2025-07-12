"""
Тесты для админ панели.
"""

import pytest
from fastapi.testclient import TestClient

from tests.test_admin_app import test_app


class TestAdminPanel:
    """Тесты для админ панели."""
    
    @pytest.fixture
    def client(self) -> TestClient:
        """Тестовый клиент для админ панели."""
        return TestClient(test_app)
    
    def test_admin_panel_health(self, client: TestClient):
        """Тест доступности админ панели."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["message"] == "Admin Panel Home"
    
    def test_healthcheck_endpoint(self, client: TestClient):
        """Тест эндпоинта проверки здоровья."""
        response = client.get("/healthcheck")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_admin_panel_notifications_list(self, client: TestClient):
        """Тест списка уведомлений."""
        response = client.get("/admin/notification/list")
        assert response.status_code == 200
        assert "notifications" in response.json()
    
    def test_admin_panel_users_list(self, client: TestClient):
        """Тест списка пользователей."""
        response = client.get("/admin/user/list")
        assert response.status_code == 200
        assert "users" in response.json()
    
    def test_admin_panel_create_notification_form(self, client: TestClient):
        """Тест формы создания уведомления."""
        response = client.get("/admin/notification/create")
        assert response.status_code == 200
        assert response.json()["form"] == "create_notification"
    
    def test_admin_panel_create_notification(self, client: TestClient):
        """Тест создания уведомления через админ панель."""
        notification_data = {"text": "Test notification from admin panel", "comment": "Test comment"}
        
        response = client.post("/admin/notification/create", data=notification_data)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Notification created"
        assert data["text"] == "Test notification from admin panel"
    
    def test_admin_panel_send_notification_action(self, client: TestClient):
        """Тест действия отправки уведомления."""
        send_data = {"action": "send_notification", "rowid": "1"}
        response = client.post("/admin/notification/action", data=send_data)
        assert response.status_code == 200
        assert "sent" in response.json()["message"]
    
    def test_admin_panel_invalid_action(self, client: TestClient):
        """Тест неверного действия."""
        send_data = {"action": "invalid_action", "rowid": "1"}
        response = client.post("/admin/notification/action", data=send_data)
        assert response.status_code == 400
        assert "detail" in response.json()
    
    def test_admin_panel_create_notification_empty_text(self, client: TestClient):
        """Тест создания уведомления с пустым текстом."""
        notification_data = {"text": "", "comment": "Test comment"}
        
        response = client.post("/admin/notification/create", data=notification_data)
        assert response.status_code == 400
        assert "detail" in response.json()
    
    def test_admin_panel_create_notification_missing_text(self, client: TestClient):
        """Тест создания уведомления без текста."""
        notification_data = {"comment": "Test comment"}
        
        response = client.post("/admin/notification/create", data=notification_data)
        assert response.status_code == 400
        assert "detail" in response.json()
    
    def test_admin_panel_send_notification_missing_id(self, client: TestClient):
        """Тест отправки уведомления без ID."""
        send_data = {"action": "send_notification"}
        response = client.post("/admin/notification/action", data=send_data)
        assert response.status_code == 400
        assert "detail" in response.json()
    
    def test_admin_panel_notification_detail(self, client: TestClient):
        """Тест детальной страницы уведомления."""
        response = client.get("/admin/notification/detail/1")
        assert response.status_code == 200
        data = response.json()
        assert data["notification_id"] == 1
        assert "text" in data
    
    def test_admin_panel_user_detail(self, client: TestClient):
        """Тест детальной страницы пользователя."""
        response = client.get("/admin/user/detail/123456789")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 123456789
        assert "username" in data
    
    def test_admin_panel_edit_notification(self, client: TestClient):
        """Тест редактирования уведомления."""
        edit_data = {"text": "Updated notification text", "comment": "Updated comment"}
        response = client.post("/admin/notification/edit/1", data=edit_data)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Notification updated"
        assert data["id"] == 1
    
    def test_admin_panel_delete_notification(self, client: TestClient):
        """Тест удаления уведомления."""
        response = client.post("/admin/notification/delete/1")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Notification deleted"
        assert data["id"] == 1 