"""
Тесты для проверки обработки ошибок при отправке уведомлений.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.exceptions import TelegramForbiddenError, TelegramAPIError

from app.services.notification_service import NotificationService, UserStatus


class CustomTelegramAPIError(TelegramAPIError):
    """Кастомный класс для тестирования ошибок с кодом."""
    
    def __init__(self, message: str, code: int):
        super().__init__(method=MagicMock(), message=message)
        self._code = code
    
    @property
    def code(self):
        return self._code


class TestNotificationErrorHandling:
    """Тесты обработки ошибок при отправке уведомлений."""

    @pytest.fixture
    def mock_bot(self):
        """Мок для бота."""
        bot = AsyncMock()
        return bot

    @pytest.fixture
    def mock_session_pool(self):
        """Мок для пула сессий."""
        session_pool = AsyncMock()
        return session_pool

    @pytest.fixture
    def notification_service(self, mock_bot, mock_session_pool):
        """Сервис уведомлений с моками."""
        return NotificationService(mock_bot, mock_session_pool)

    @pytest.mark.asyncio
    async def test_user_blocked_error(self, notification_service, mock_bot):
        """Тест обработки ошибки блокировки бота пользователем."""
        # Настраиваем мок для имитации ошибки блокировки
        mock_bot.send_message.side_effect = TelegramForbiddenError(
            method=MagicMock(), message="Forbidden: bot was blocked by the user"
        )

        # Вызываем метод отправки
        result = await notification_service.send_notification_to_user(123, "Test message")

        # Проверяем результат
        assert result["success"] is False
        assert result["user_id"] == 123
        assert result["error_type"] == "user_blocked"
        assert "заблокировал бота" in result["message"]
        assert result["should_retry"] is False

    @pytest.mark.asyncio
    async def test_chat_not_found_error(self, notification_service, mock_bot):
        """Тест обработки ошибки несуществующего чата."""
        # Настраиваем мок для имитации ошибки несуществующего чата
        error = CustomTelegramAPIError("Bad Request: chat not found", code=400)
        mock_bot.send_message.side_effect = error

        # Вызываем метод отправки
        result = await notification_service.send_notification_to_user(456, "Test message")

        # Проверяем результат
        assert result["success"] is False
        assert result["user_id"] == 456
        assert result["error_type"] == "chat_not_found"
        assert "не найден" in result["message"]
        assert result["should_retry"] is False

    @pytest.mark.asyncio
    async def test_user_deactivated_error(self, notification_service, mock_bot):
        """Тест обработки ошибки деактивированного пользователя."""
        # Настраиваем мок для имитации ошибки деактивированного пользователя
        error = CustomTelegramAPIError("Bad Request: user is deactivated", code=400)
        mock_bot.send_message.side_effect = error

        # Вызываем метод отправки
        result = await notification_service.send_notification_to_user(789, "Test message")

        # Проверяем результат
        assert result["success"] is False
        assert result["user_id"] == 789
        assert result["error_type"] == "user_deactivated"
        assert "деактивирован" in result["message"]
        assert result["should_retry"] is False

    @pytest.mark.asyncio
    async def test_rate_limit_error(self, notification_service, mock_bot):
        """Тест обработки ошибки превышения лимита отправки."""
        # Настраиваем мок для имитации ошибки превышения лимита
        error = CustomTelegramAPIError("Too Many Requests: retry after 30", code=429)
        mock_bot.send_message.side_effect = error

        # Вызываем метод отправки
        result = await notification_service.send_notification_to_user(101, "Test message")

        # Проверяем результат
        assert result["success"] is False
        assert result["user_id"] == 101
        assert result["error_type"] == "rate_limit"
        assert "лимит отправки" in result["message"]
        assert result["should_retry"] is True

    @pytest.mark.asyncio
    async def test_server_error(self, notification_service, mock_bot):
        """Тест обработки ошибки сервера Telegram."""
        # Настраиваем мок для имитации ошибки сервера
        error = CustomTelegramAPIError("Internal Server Error", code=500)
        mock_bot.send_message.side_effect = error

        # Вызываем метод отправки
        result = await notification_service.send_notification_to_user(202, "Test message")

        # Проверяем результат
        assert result["success"] is False
        assert result["user_id"] == 202
        assert result["error_type"] == "server_error"
        assert "сервера Telegram" in result["message"]
        assert result["should_retry"] is True

    @pytest.mark.asyncio
    async def test_unknown_error(self, notification_service, mock_bot):
        """Тест обработки неизвестной ошибки."""
        # Настраиваем мок для имитации неизвестной ошибки
        error = CustomTelegramAPIError("Unknown error occurred", code=999)
        mock_bot.send_message.side_effect = error

        # Вызываем метод отправки
        result = await notification_service.send_notification_to_user(303, "Test message")

        # Проверяем результат
        assert result["success"] is False
        assert result["user_id"] == 303
        assert result["error_type"] == "unknown_error"
        assert "Неизвестная ошибка" in result["message"]
        assert result["should_retry"] is True

    @pytest.mark.asyncio
    async def test_successful_send(self, notification_service, mock_bot):
        """Тест успешной отправки уведомления."""
        # Настраиваем мок для успешной отправки
        mock_bot.send_message.return_value = MagicMock()

        # Вызываем метод отправки
        result = await notification_service.send_notification_to_user(404, "Test message")

        # Проверяем результат
        assert result["success"] is True
        assert result["user_id"] == 404
        assert result["error_type"] is None
        assert result["message"] == "Уведомление отправлено"

    @pytest.mark.asyncio
    async def test_user_status_enum(self):
        """Тест перечисления статусов пользователей."""
        assert UserStatus.ACTIVE.value == "active"
        assert UserStatus.BLOCKED.value == "blocked"
        assert UserStatus.INACTIVE.value == "inactive"
        assert UserStatus.DELETED.value == "deleted"

    @pytest.mark.asyncio
    async def test_error_handling_with_user_status_update(self, notification_service, mock_bot, mock_session_pool):
        """Тест обновления статуса пользователя при ошибке."""
        mock_bot.send_message.side_effect = TelegramForbiddenError(
            method=MagicMock(), message="Forbidden: bot was blocked by the user"
        )

        mock_users = MagicMock()
        mock_users.update_user_status = AsyncMock(return_value=MagicMock())
        mock_repository = MagicMock()
        mock_repository.users = mock_users
        mock_uow = MagicMock()

        # Патчим SQLSessionContext только для этого теста
        with patch("app.services.notification_service.SQLSessionContext") as SQLSessionContextMock:
            cm = AsyncMock()
            cm.__aenter__.return_value = (mock_repository, mock_uow)
            SQLSessionContextMock.return_value = cm

            result = await notification_service.send_notification_to_user(505, "Test message")

            assert result["success"] is False
            assert result["error_type"] == "user_blocked"
            mock_users.update_user_status.assert_called_once_with(505, "blocked") 