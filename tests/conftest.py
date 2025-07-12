"""
Конфигурация pytest для тестов админ панели.
"""

import os
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from tests.test_admin_app import test_app


@pytest.fixture
def test_config():
    """Конфигурация для тестов."""
    os.environ.update({
        "TELEGRAM_BOT_TOKEN": "test_token",
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5433",
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


@pytest.fixture
def admin_client() -> TestClient:
    """Тестовый клиент для админ панели."""
    return TestClient(test_app)


@pytest.fixture
def mock_session_pool():
    """Мок пула сессий для тестов."""
    session_pool = MagicMock()
    session_pool.return_value.__aenter__ = MagicMock()
    session_pool.return_value.__aexit__ = MagicMock()
    return session_pool


@pytest.fixture
def mock_redis_repository():
    """Мок Redis репозитория для тестов."""
    repository = MagicMock()
    repository.get = MagicMock()
    repository.set = MagicMock()
    repository.delete = MagicMock()
    repository.exists = MagicMock(return_value=False)
    repository.close = MagicMock()
    return repository


@pytest.fixture
def mock_bot():
    """Мок Telegram бота для тестов."""
    bot = MagicMock()
    bot.send_message = MagicMock()
    return bot


@pytest.fixture
def mock_dispatcher():
    """Мок диспетчера для тестов."""
    dispatcher = MagicMock()
    return dispatcher 