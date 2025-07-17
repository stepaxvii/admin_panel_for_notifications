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


# noinspection PyArgumentList
def create_app_config() -> AppConfig:
    return AppConfig(
        telegram=TelegramConfig(),  # type: ignore
        postgres=PostgresConfig(),  # type: ignore
        sql_alchemy=SQLAlchemyConfig(),  # type: ignore
        redis=RedisConfig(),  # type: ignore
        server=ServerConfig(),  # type: ignore
        common=CommonConfig(),  # type: ignore
    )
