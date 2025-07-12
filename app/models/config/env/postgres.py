"""
Конфигурация PostgreSQL базы данных.

Настройки подключения и параметры базы данных.
"""

from pydantic import SecretStr
from sqlalchemy import URL

from .base import EnvSettings


class PostgresConfig(EnvSettings, env_prefix="POSTGRES_"):
    """Конфигурация PostgreSQL базы данных."""
    
    host: str = "localhost"
    db: str = "postgres"
    password: SecretStr = SecretStr("password")
    port: int = 5432
    user: str = "postgres"
    data: str = "/var/lib/postgresql/data"

    def build_url(self) -> URL:
        """Создает URL для подключения к базе данных."""
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.user,
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            database=self.db,
        )
