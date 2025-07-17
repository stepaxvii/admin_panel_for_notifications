from pydantic import BaseModel

from app.models.config.env.common import CommonConfig
from app.models.config.env.postgres import PostgresConfig
from app.models.config.env.redis import RedisConfig
from app.models.config.env.server import ServerConfig
from app.models.config.env.sql_alchemy import SQLAlchemyConfig
from app.models.config.env.telegram import TelegramConfig


class AppConfig(BaseModel):
    telegram: TelegramConfig
    postgres: PostgresConfig
    sql_alchemy: SQLAlchemyConfig
    redis: RedisConfig
    server: ServerConfig
    common: CommonConfig
