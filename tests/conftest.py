import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.factory import create_app_config, create_bot, create_dispatcher
from app.factory.telegram.fastapi import setup_fastapi


@pytest.fixture(scope="session")
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
