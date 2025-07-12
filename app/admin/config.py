"""
Конфигурация админ-панели.

Содержит настройки базы данных, логирования и другие параметры
для работы админ-панели.
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine
from app.utils.logging import setup_logger

# Настройки логирования
JSON_FORMAT = True

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

# Настройки админ-панели
ADMIN_TITLE = "Панель управления ботом"
ADMIN_BASE_URL = "/"
ADMIN_PORT = 9000
ADMIN_HOST = "0.0.0.0"


def setup_admin_logging():
    """Настраивает логирование для админ-панели."""
    setup_logger(
        log_file="logs/admin.log",
        json_format=JSON_FORMAT
    )


def create_database_engine():
    """Создает движок базы данных для админ-панели."""
    return create_async_engine(
        DATABASE_URL,
        echo=ALCHEMY_ECHO,
        pool_pre_ping=True,
        pool_recycle=ALCHEMY_POOL_RECYCLE,
        pool_size=ALCHEMY_POOL_SIZE,
        max_overflow=ALCHEMY_MAX_OVERFLOW,
        pool_timeout=ALCHEMY_POOL_TIMEOUT,
    ) 