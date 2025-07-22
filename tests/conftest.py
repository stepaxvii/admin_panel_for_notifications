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


@pytest_asyncio.fixture(autouse=True)
async def cleanup_notifications(test_client):
    yield
    # Очистка уведомлений после каждого теста
    response = await test_client.get("/notifications/")
    if response.status_code == 200:
        for notification in response.json():
            await test_client.delete(f"/notifications/{notification['id']}")
