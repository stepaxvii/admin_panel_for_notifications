"""
Интеграционные тесты для админ панели.
"""

import pytest
from fastapi.testclient import TestClient

from tests.test_admin_app import test_app


class TestAdminIntegration:
    """Интеграционные тесты для админ панели."""
    
    @pytest.fixture
    def client(self) -> TestClient:
        """Тестовый клиент для админ панели."""
        return TestClient(test_app)
    
    def test_full_notification_workflow(self, client: TestClient):
        """Тест полного рабочего процесса уведомлений."""
        # 1. Создаем уведомление
        notification_data = {
            "text": "Integration test notification",
            "comment": "Full workflow test"
        }
        
        create_response = client.post("/admin/notification/create", data=notification_data)
        assert create_response.status_code == 200
        
        # 2. Проверяем, что уведомление появилось в списке
        list_response = client.get("/admin/notification/list")
        assert list_response.status_code == 200
        
        # 3. Отправляем уведомление
        send_data = {
            "action": "send_notification",
            "rowid": "1"
        }
        send_response = client.post("/admin/notification/action", data=send_data)
        assert send_response.status_code == 200

    def test_notification_via_api_then_view_in_admin(self, client: TestClient):
        """Тест создания уведомления через API и просмотра в админ панели."""
        # 1. Создаем уведомление через API
        api_notification_data = {
            "text": "API created notification",
            "comment": "API test",
            "user_ids": [123456789]
        }
        
        api_response = client.post("/api/notifications/send", json=api_notification_data)
        assert api_response.status_code == 200
        
        # 2. Проверяем, что уведомление появилось в админ панели
        admin_list_response = client.get("/admin/notification/list")
        assert admin_list_response.status_code == 200

    def test_user_management_workflow(self, client: TestClient):
        """Тест рабочего процесса управления пользователями."""
        # 1. Получаем список пользователей
        users_response = client.get("/admin/user/list")
        assert users_response.status_code == 200
        
        # 2. Получаем список пользователей через API
        api_users_response = client.get("/api/users")
        assert api_users_response.status_code == 200
        
        # 3. Проверяем детальную страницу пользователя
        user_detail_response = client.get("/admin/user/detail/123456789")
        assert user_detail_response.status_code == 200

    def test_notification_validation_workflow(self, client: TestClient):
        """Тест рабочего процесса валидации уведомлений."""
        # 1. Пытаемся создать уведомление с пустым текстом
        empty_text_data = {
            "text": "",
            "comment": "Empty text test"
        }
        empty_response = client.post("/admin/notification/create", data=empty_text_data)
        assert empty_response.status_code == 400
        
        # 2. Пытаемся создать уведомление без текста
        no_text_data = {
            "comment": "No text test"
        }
        no_text_response = client.post("/admin/notification/create", data=no_text_data)
        assert no_text_response.status_code == 400
        
        # 3. Создаем корректное уведомление
        valid_data = {
            "text": "Valid notification",
            "comment": "Valid test"
        }
        valid_response = client.post("/admin/notification/create", data=valid_data)
        assert valid_response.status_code == 200

    def test_notification_actions_workflow(self, client: TestClient):
        """Тест рабочего процесса действий с уведомлениями."""
        # 1. Создаем уведомление
        notification_data = {
            "text": "Actions test notification",
            "comment": "Actions test"
        }
        create_response = client.post("/admin/notification/create", data=notification_data)
        assert create_response.status_code == 200
        
        # 2. Пытаемся выполнить неверное действие
        invalid_action_data = {
            "action": "invalid_action",
            "rowid": "1"
        }
        invalid_action_response = client.post("/admin/notification/action", data=invalid_action_data)
        assert invalid_action_response.status_code == 400
        
        # 3. Отправляем корректное уведомление
        valid_send_data = {
            "action": "send_notification",
            "rowid": "1"
        }
        valid_send_response = client.post("/admin/notification/action", data=valid_send_data)
        assert valid_send_response.status_code == 200

    def test_api_error_handling_workflow(self, client: TestClient):
        """Тест рабочего процесса обработки ошибок API."""
        # 1. Пытаемся отправить уведомление с неверными данными
        invalid_api_data = {
            "text": "",
            "user_ids": [123456789]
        }
        invalid_api_response = client.post("/api/notifications/send", json=invalid_api_data)
        assert invalid_api_response.status_code == 400
        
        # 2. Пытаемся использовать неверный HTTP метод
        invalid_method_response = client.put("/api/notifications/send")
        assert invalid_method_response.status_code == 405
        
        # 3. Пытаемся обратиться к несуществующему эндпоинту
        invalid_endpoint_response = client.get("/api/invalid/endpoint")
        assert invalid_endpoint_response.status_code == 404

    def test_admin_panel_navigation_workflow(self, client: TestClient):
        """Тест навигации по админ панели."""
        # 1. Главная страница
        home_response = client.get("/")
        assert home_response.status_code == 200
        
        # 2. Список уведомлений
        notifications_response = client.get("/admin/notification/list")
        assert notifications_response.status_code == 200
        
        # 3. Список пользователей
        users_response = client.get("/admin/user/list")
        assert users_response.status_code == 200
        
        # 4. Форма создания уведомления
        create_form_response = client.get("/admin/notification/create")
        assert create_form_response.status_code == 200

    def test_data_consistency_workflow(self, client: TestClient):
        """Тест согласованности данных между API и админ панелью."""
        # 1. Создаем уведомление через админ панель
        admin_notification_data = {
            "text": "Consistency test notification",
            "comment": "Consistency test"
        }
        admin_create_response = client.post("/admin/notification/create", data=admin_notification_data)
        assert admin_create_response.status_code == 200
        
        # 2. Проверяем, что уведомление доступно через API
        api_list_response = client.get("/api/notifications")
        assert api_list_response.status_code == 200
        
        # 3. Создаем уведомление через API
        api_notification_data = {
            "text": "API consistency test notification",
            "comment": "API consistency test",
            "user_ids": [123456789]
        }
        api_create_response = client.post("/api/notifications/send", json=api_notification_data)
        assert api_create_response.status_code == 200
        
        # 4. Проверяем, что уведомление доступно в админ панели
        admin_list_response = client.get("/admin/notification/list")
        assert admin_list_response.status_code == 200

    def test_notification_crud_workflow(self, client: TestClient):
        """Тест полного CRUD рабочего процесса уведомлений."""
        # 1. Создаем уведомление
        create_data = {
            "text": "CRUD test notification",
            "comment": "CRUD test"
        }
        create_response = client.post("/admin/notification/create", data=create_data)
        assert create_response.status_code == 200
        
        # 2. Читаем детальную информацию
        detail_response = client.get("/admin/notification/detail/1")
        assert detail_response.status_code == 200
        
        # 3. Обновляем уведомление
        update_data = {
            "text": "Updated CRUD test notification",
            "comment": "Updated CRUD test"
        }
        update_response = client.post("/admin/notification/edit/1", data=update_data)
        assert update_response.status_code == 200
        
        # 4. Удаляем уведомление
        delete_response = client.post("/admin/notification/delete/1")
        assert delete_response.status_code == 200 