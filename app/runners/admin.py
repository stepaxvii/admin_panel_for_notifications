"""
Админ-панель для управления Telegram ботом.

Предоставляет веб-интерфейс для создания и отправки уведомлений пользователям бота.
"""

from env_loader import auto_env_patch
auto_env_patch()

import os
import time
import subprocess
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette_admin.contrib.sqla import Admin, ModelView
from starlette_admin import action
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select
import socket
from datetime import datetime
from sqlalchemy import update

from app.models.sql.base import Base
from app.models.sql.notification import Notification
from app.factory.telegram.bot import create_bot
from app.factory.telegram.dispatcher import create_dispatcher
from app.factory.app_config import create_app_config
from app.endpoints.notifications import router as notifications_router
from app.utils.logging import admin as logger, setup_logger
from app.models.sql.user import User

# Удаляю функцию is_elasticsearch_available и все проверки доступности Elasticsearch

# Вместо проверки всегда включаю json_format=True
json_format = True  # JSON формат для Elasticsearch/Filebeat

# Инициализация логирования
setup_logger(
    log_file="logs/admin.log",
    json_format=json_format
)

# Конфигурация базы данных
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")

# Настройки SQLAlchemy
ALCHEMY_ECHO = os.getenv("ALCHEMY_ECHO", "False").lower() == "true"
ALCHEMY_POOL_SIZE = int(os.getenv("ALCHEMY_POOL_SIZE", "10"))
ALCHEMY_MAX_OVERFLOW = int(os.getenv("ALCHEMY_MAX_OVERFLOW", "20"))
ALCHEMY_POOL_TIMEOUT = int(os.getenv("ALCHEMY_POOL_TIMEOUT", "10"))
ALCHEMY_POOL_RECYCLE = int(os.getenv("ALCHEMY_POOL_RECYCLE", "3600"))

DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

logger.info(f"Подключение к базе данных: {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")

# Создание движка базы данных
engine = create_async_engine(
    DATABASE_URL,
    echo=ALCHEMY_ECHO,
    pool_pre_ping=True,
    pool_recycle=ALCHEMY_POOL_RECYCLE,
    pool_size=ALCHEMY_POOL_SIZE,
    max_overflow=ALCHEMY_MAX_OVERFLOW,
    pool_timeout=ALCHEMY_POOL_TIMEOUT,
)

# Инициализация компонентов
config = create_app_config()
bot = create_bot(config)
dispatcher = create_dispatcher(config)

from app.factory.session_pool import create_session_pool
session_pool = create_session_pool(config=config)


def run_alembic_upgrade() -> None:
    """Применяет миграции Alembic к базе данных."""
    try:
        logger.info("Применение миграций Alembic...")
        result = subprocess.run(["alembic", "upgrade", "head"], check=True, capture_output=True, text=True)
        logger.info(f"[alembic stdout]\n{result.stdout}")
        if result.stderr:
            logger.warning(f"[alembic stderr]\n{result.stderr}")
    except subprocess.CalledProcessError as e:
        logger.error(f"[alembic ERROR] Код возврата: {e.returncode}")
        logger.error(f"[alembic stdout]\n{e.stdout}")
        logger.error(f"[alembic stderr]\n{e.stderr}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Ошибка применения миграций: {e}")
        sys.exit(1)


run_alembic_upgrade()


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


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Middleware для мониторинга производительности запросов."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    if process_time > 1.0:
        logger.warning(f"МЕДЛЕННЫЙ ЗАПРОС: {request.url.path} - {process_time:.2f}с")
    else:
        logger.debug(f"ПРОИЗВОДИТЕЛЬНОСТЬ: {request.url.path} - {process_time:.2f}с")
    
    return response


@app.get("/health")
async def health_check():
    """Проверка состояния админ-панели."""
    return {
        "status": "ok", 
        "message": "Админ-панель работает",
        "database": f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    }


app.include_router(notifications_router)


# Создание админ-панели
admin = Admin(
    engine,
    title="Панель управления ботом",
    base_url="/",
    auth_provider=None,
)


class NotificationView(ModelView):
    """Представление модели уведомлений в админ-панели."""
    
    name = "Уведомление"
    name_plural = "Уведомления"
    icon = "fa fa-bell"
    
    can_export = False
    can_set_page_size = False
    page_size = 20
    
    column_list = ["id", "text", "comment", "status", "error", "created_at", "sent_at"]
    column_searchable_list = ["text", "comment"]
    column_sortable_list = ["id", "status", "created_at", "sent_at"]
    
    column_labels = {
        "id": "ID",
        "text": "Текст",
        "comment": "Комментарий",
        "status": "Статус",
        "error": "Ошибка",
        "created_at": "Создано",
        "sent_at": "Отправлено",
    }
    
    form_labels = {
        "text": "Текст уведомления",
        "comment": "Комментарий (необязательно)",
    }
    
    form_include_pk = False
    form_excluded_columns = ["id", "status", "error", "sent_at", "created_at", "updated_at"]
    form_columns = ["text", "comment"]
    
    form_widget_args = {
        "text": {"rows": 5, "placeholder": "Введите текст уведомления..."},
        "comment": {"rows": 3, "placeholder": "Введите комментарий (необязательно)..."}
    }
    
    def get_form_fields(self, request: Request) -> list:
        """Возвращает поля для формы."""
        return ["text", "comment"]
    
    def get_create_form_fields(self, request: Request) -> list:
        """Возвращает поля для формы создания."""
        return ["text", "comment"]
    
    def get_edit_form_fields(self, request: Request) -> list:
        """Возвращает поля для формы редактирования."""
        return ["text", "comment"]
    
    @action(
        name="preview_notification",
        text="Предпросмотр",
        confirmation=None,
        submit_btn_text="Закрыть",
        submit_btn_class="btn-secondary",
    )
    async def preview_notification_action(self, request: Request, pks: list) -> str:
        """Показывает предпросмотр уведомления."""
        if not pks:
            return "Не выбрано ни одного уведомления."
        
        try:
            pk = int(pks[0])
        except (ValueError, TypeError):
            return f"Неверный ID уведомления: {pks[0]}"
        
        async with engine.begin() as conn:
            stmt = select(*Notification.__table__.c).filter_by(id=pk)
            result = await conn.execute(stmt)
            row = result.first()
            
            if row:
                notification = Notification(**row._asdict())
            else:
                notification = None
            
            if not notification or not hasattr(notification, 'id'):
                return f"Ошибка: не удалось получить объект уведомления с ID {pk}"
            
            preview = f"""
            <div style="font-family: Arial, sans-serif; padding: 20px;">
                <h3>Предпросмотр уведомления #{notification.id}</h3>
                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0;">
                    <strong>Текст:</strong><br>
                    <pre style="white-space: pre-wrap; word-wrap: break-word;">{notification.text}</pre>
                </div>
                <div style="margin: 10px 0;">
                    <strong>Статус:</strong> {notification.status}<br>
                    <strong>Создано:</strong> {notification.created_at.strftime('%Y-%m-%d %H:%M:%S') if notification.created_at else 'Не указано'}<br>
                    <strong>Отправлено:</strong> {notification.sent_at.strftime('%Y-%m-%d %H:%M:%S') if notification.sent_at else 'Не отправлено'}
                </div>
                {f'<div style="color: red; margin: 10px 0;"><strong>Ошибка:</strong> {notification.error}</div>' if notification.error else ''}
            </div>
            """
            return preview

    @action(
        name="send_notification",
        text="Отправить уведомление",
        confirmation="Вы уверены, что хотите отправить это уведомление всем пользователям?",
        submit_btn_text="Да, отправить",
        submit_btn_class="btn-primary",
    )
    async def send_notification_action(self, request: Request, pks: list) -> str:
        """Отправляет уведомление всем активным пользователям."""
        try:
            notification_ids = []
            for pk in pks:
                try:
                    notification_ids.append(int(pk))
                except (ValueError, TypeError):
                    return f"Неверный ID уведомления: {pk}"
            
            results = []
            async with app.state.session_pool() as session:
                for pk in notification_ids:
                    # Получаем уведомление из базы
                    response = await session.execute(
                        select(Notification).filter_by(id=pk)
                    )
                    notification = response.scalar_one_or_none()
                    
                    if not notification:
                        results.append(f"❌ Уведомление {pk}: Уведомление не найдено")
                        continue
                    
                    try:
                        # Получаем всех активных пользователей
                        users_response = await session.execute(
                            select(User).filter(User.blocked_at.is_(None))
                        )
                        users = users_response.scalars().all()
                        
                        if not users:
                            results.append(f"❌ Уведомление {pk}: Нет активных пользователей")
                            continue
                        
                        # Отправляем уведомление каждому пользователю
                        sent_count = 0
                        error_count = 0
                        
                        for user in users:
                            try:
                                await app.state.bot.send_message(
                                    chat_id=user.id,
                                    text=notification.text
                                )
                                sent_count += 1
                            except Exception as e:
                                error_count += 1
                                logger.error(f"Ошибка отправки уведомления {pk} пользователю {user.id}: {e}")
                        
                        # Обновляем статус уведомления
                        await session.execute(
                            update(Notification)
                            .where(Notification.id == pk)
                            .values(
                                status="sent",
                                sent_at=datetime.utcnow(),
                                error=f"Ошибок: {error_count}" if error_count > 0 else None
                            )
                        )
                        await session.commit()
                        
                        results.append(f"✅ Уведомление {pk}: {sent_count} отправлено, {error_count} ошибок")
                        
                    except Exception as e:
                        # Обновляем статус уведомления с ошибкой
                        await session.execute(
                            update(Notification)
                            .where(Notification.id == pk)
                            .values(
                                status="error",
                                error=str(e)
                            )
                        )
                        await session.commit()
                        
                        results.append(f"❌ Уведомление {pk}: Ошибка отправки - {str(e)}")
            
            return "<br>".join(results)
        except Exception as e:
            return f"Ошибка при отправке: {str(e)}"


admin.add_view(NotificationView(Notification))
admin.mount_to(app)

# Монтирование статических файлов Starlette Admin
import starlette_admin
static_path = os.path.join(os.path.dirname(starlette_admin.__file__), "statics")
app.mount("/statics", StaticFiles(directory=static_path), name="statics")


if __name__ == "__main__":
    import uvicorn
    logger.info("Запуск админ-панели на http://0.0.0.0:9000")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9000,
        log_level="info",
        access_log=True,
        workers=1
    ) 