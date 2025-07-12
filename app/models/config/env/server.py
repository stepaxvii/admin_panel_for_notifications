"""
Конфигурация веб-сервера.

Настройки хоста, порта и URL сервера.
"""

from .base import EnvSettings


class ServerConfig(EnvSettings, env_prefix="SERVER_"):
    """Конфигурация веб-сервера."""
    
    port: int = 8000
    host: str = "0.0.0.0"
    url: str = "http://localhost:8000"

    def build_url(self, path: str) -> str:
        """Создает полный URL для указанного пути."""
        return f"{self.url}{path}"
