"""
Фабрика для создания конфигурации приложения.

Создает и настраивает все компоненты конфигурации из переменных окружения.
"""

from __future__ import annotations

from app.models.config.env import (
    AppConfig,
    CommonConfig,
    PostgresConfig,
    RedisConfig,
    ServerConfig,
    SQLAlchemyConfig,
    TelegramConfig,
)


def create_app_config() -> AppConfig:
    """Создает полную конфигурацию приложения из переменных окружения."""
    return AppConfig(
        telegram=TelegramConfig(),
        postgres=PostgresConfig(),
        sql_alchemy=SQLAlchemyConfig(),
        redis=RedisConfig(),
        server=ServerConfig(),
        common=CommonConfig(),
    )
