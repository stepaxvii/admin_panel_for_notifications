"""
Модуль логирования для приложения.

Предоставляет настроенные логгеры для разных компонентов системы.
"""

import logging

from .setup import disable_aiogram_logs, setup_logger, get_logger

__all__ = [
    "database",
    "admin",
    "bot",
    "notifications",
    "redis",
    "disable_aiogram_logs",
    "setup_logger",
    "get_logger",
]

# Специализированные логгеры для разных компонентов
database: logging.Logger = logging.getLogger("bot.database")
admin: logging.Logger = logging.getLogger("bot.admin")
bot: logging.Logger = logging.getLogger("bot.telegram")
notifications: logging.Logger = logging.getLogger("bot.notifications")
redis: logging.Logger = logging.getLogger("bot.redis")
