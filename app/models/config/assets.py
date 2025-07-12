"""
Конфигурация ресурсов приложения.

Настройки для команд и других ресурсов бота.
"""

from app.utils.yaml import YAMLSettings


class Assets(YAMLSettings):
    """Конфигурация ресурсов приложения."""
    
    commands: dict[str, list[dict[str, str]]] = {}
