"""
Общая конфигурация приложения.

Общие настройки, используемые во всем приложении.
"""

from .base import EnvSettings


class CommonConfig(EnvSettings, env_prefix="COMMON_"):
    """Общая конфигурация приложения."""
    
    admin_chat_id: int = 0
