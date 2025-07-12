"""
Конфигурация Redis кэша.

Настройки подключения к Redis серверу.
"""

from pydantic import SecretStr

from .base import EnvSettings


class RedisConfig(EnvSettings, env_prefix="REDIS_"):
    """Конфигурация Redis кэша."""
    
    host: str = "localhost"
    password: SecretStr = SecretStr("")
    port: int = 6379
    db: int = 0

    def build_url(self) -> str:
        """Создает URL для подключения к Redis."""
        return f"redis://:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.db}"
