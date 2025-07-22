import pytest
import pytest_asyncio
from unittest.mock import AsyncMock

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.factory import create_app_config, create_bot, create_dispatcher
from app.factory.telegram.fastapi import setup_fastapi


@pytest.fixture(scope="function")
def test_app():
    config = create_app_config()
    bot = create_bot(config)
    dispatcher = create_dispatcher(config)
    app = FastAPI()
    setup_fastapi(app=app, dispatcher=dispatcher, bot=bot)
    return app


@pytest_asyncio.fixture
async def test_client(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
def mock_external_services(mocker):
    mock_redis = AsyncMock()
    mocker.patch("app.factory.redis.create_redis", return_value=mock_redis)
    mock_session_pool = AsyncMock()
    mocker.patch("app.factory.session_pool.create_session_pool", return_value=mock_session_pool)
    mocker.patch(
        "app.services.crud.notification.NotificationService.list_all",
        new_callable=AsyncMock,
        return_value=[{"id": 1, "text": "Test create", "comment": "Test create"}]
    )
    mocker.patch(
        "app.services.crud.notification.NotificationService.create",
        new_callable=AsyncMock,
        return_value={"id": 1, "text": "Test create", "comment": "Test create"}
    )
    mocker.patch(
        "app.services.crud.notification.NotificationService.get",
        new_callable=AsyncMock,
        return_value={"id": 1, "text": "Test create", "comment": "Test create"}
    )
    mocker.patch(
        "app.services.crud.notification.NotificationService.update",
        new_callable=AsyncMock,
        return_value={"id": 1, "text": "Edited complite", "comment": "Test edit"}
    )
    mocker.patch(
        "app.services.crud.notification.NotificationService.delete",
        new_callable=AsyncMock,
        return_value=None
    )
