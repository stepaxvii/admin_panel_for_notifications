"""
Тесты производительности для админ панели.
"""

import time
import pytest
from fastapi.testclient import TestClient

from tests.test_admin_app import test_app


class TestAdminPerformance:
    """Тесты производительности админ панели."""
    
    @pytest.fixture
    def client(self) -> TestClient:
        """Тестовый клиент для админ панели."""
        return TestClient(test_app)
    
    def test_admin_panel_response_time(self, client: TestClient):
        """Тест времени отклика админ панели."""
        start_time = time.time()
        response = client.get("/")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 1.0  # Должно отвечать менее чем за 1 секунду
    
    def test_notifications_list_response_time(self, client: TestClient):
        """Тест времени отклика списка уведомлений."""
        start_time = time.time()
        response = client.get("/admin/notification/list")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 2.0  # Должно отвечать менее чем за 2 секунды
    
    def test_users_list_response_time(self, client: TestClient):
        """Тест времени отклика списка пользователей."""
        start_time = time.time()
        response = client.get("/admin/user/list")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 2.0  # Должно отвечать менее чем за 2 секунды
    
    def test_create_notification_response_time(self, client: TestClient):
        """Тест времени отклика создания уведомления."""
        notification_data = {
            "text": "Performance test notification",
            "comment": "Test comment"
        }
        
        start_time = time.time()
        response = client.post("/admin/notification/create", data=notification_data)
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 3.0  # Должно отвечать менее чем за 3 секунды
    
    def test_send_notification_response_time(self, client: TestClient):
        """Тест времени отклика отправки уведомления."""
        send_data = {
            "action": "send_notification",
            "rowid": "1"
        }
        
        start_time = time.time()
        response = client.post("/admin/notification/action", data=send_data)
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 5.0  # Должно отвечать менее чем за 5 секунд
    
    def test_concurrent_requests(self, client: TestClient):
        """Тест одновременных запросов."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            start_time = time.time()
            response = client.get("/")
            end_time = time.time()
            results.put((response.status_code, end_time - start_time))
        
        # Запускаем 5 одновременных запросов
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Ждем завершения всех потоков
        for thread in threads:
            thread.join()
        
        # Проверяем результаты
        while not results.empty():
            status_code, response_time = results.get()
            assert status_code == 200
            assert response_time < 2.0  # Каждый запрос должен отвечать менее чем за 2 секунды
    
    def test_multiple_notifications_creation(self, client: TestClient):
        """Тест создания множественных уведомлений."""
        start_time = time.time()
        
        for i in range(10):
            notification_data = {
                "text": f"Performance test notification {i}",
                "comment": f"Test comment {i}"
            }
            response = client.post("/admin/notification/create", data=notification_data)
            assert response.status_code == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        assert total_time < 10.0  # 10 уведомлений должны создаться менее чем за 10 секунд
    
    def test_multiple_api_requests(self, client: TestClient):
        """Тест множественных API запросов."""
        start_time = time.time()
        
        for i in range(10):
            notification_data = {
                "text": f"API test notification {i}",
                "comment": f"API test {i}",
                "user_ids": [123456789 + i]
            }
            response = client.post("/api/notifications/send", json=notification_data)
            assert response.status_code == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        assert total_time < 10.0  # 10 API запросов должны выполниться менее чем за 10 секунд 