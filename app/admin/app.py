"""
Основное приложение админ-панели.

Создает и настраивает FastAPI приложение с админ-панелью.
"""

import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette_admin.contrib.sqla import Admin

from env_loader import auto_env_patch
from app.factory.telegram.bot import create_bot
from app.factory.telegram.dispatcher import create_dispatcher
from app.factory.app_config import create_app_config
from app.factory.session_pool import create_session_pool
from app.endpoints.notifications import router as notifications_router
from app.admin.config import setup_admin_logging, create_database_engine, ADMIN_TITLE, ADMIN_BASE_URL
from app.admin.utils import run_alembic_upgrade
from app.admin.middleware import performance_middleware
from app.admin.views import NotificationView, UserView
from app.models.sql.notification import Notification
from app.models.sql.user import User
from app.utils.logging import admin as logger


def create_admin_app() -> FastAPI:
    """Создает и настраивает FastAPI приложение с админ-панелью."""
    
    # Инициализация переменных окружения
    auto_env_patch()
    
    # Настройка логирования
    setup_admin_logging()
    
    # Создание движка базы данных
    engine = create_database_engine()
    
    # Применение миграций
    run_alembic_upgrade()
    
    # Инициализация компонентов
    config = create_app_config()
    bot = create_bot(config)
    dispatcher = create_dispatcher(config)
    session_pool = create_session_pool(config=config)
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Управляет жизненным циклом приложения."""
        logger.info("Запуск админ-панели...")
        start_time = time.time()
        
        try:
            logger.info(f"База данных готова за {time.time() - start_time:.2f}с")
        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
            raise
        
        yield
        
        logger.info("Завершение работы админ-панели...")
        await engine.dispose()
    
    # Создание FastAPI приложения
    app = FastAPI(lifespan=lifespan)
    
    # Состояние приложения
    app.state.bot = bot
    app.state.dispatcher = dispatcher
    app.state.session_pool = session_pool
    app.state.engine = engine
    
    # Middleware
    app.middleware("http")(performance_middleware)
    
    # Эндпоинты
    @app.get("/health")
    async def health_check():
        """Проверка состояния админ-панели."""
        return {
            "status": "ok", 
            "message": "Админ-панель работает",
            "database": f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
        }
    
    # Подключение роутеров
    app.include_router(notifications_router)
    
    # Создание админ-панели
    admin = Admin(
        engine,
        title=ADMIN_TITLE,
        base_url=ADMIN_BASE_URL,
        auth_provider=None,
    )
    
    # Добавление представлений
    admin.add_view(NotificationView(Notification))
    admin.add_view(UserView(User))
    
    # Монтирование админ-панели
    admin.mount_to(app)
    
    # Монтирование статических файлов Starlette Admin
    import starlette_admin
    static_path = os.path.join(os.path.dirname(starlette_admin.__file__), "statics")
    app.mount("/statics", StaticFiles(directory=static_path), name="statics")
    
    return app


def run_admin_app():
    """Запускает админ-панель."""
    import uvicorn
    
    app = create_admin_app()
    
    logger.info("Запуск админ-панели на http://0.0.0.0:9000")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9000,
        log_level="info",
        access_log=True,
        workers=1
    )


if __name__ == "__main__":
    run_admin_app() 