"""
Конфигурация Telegram бота.

Настройки бота, вебхуков и локализации.
"""

from typing import Optional
from pydantic import SecretStr

from app.utils.custom_types import StringList

from .base import EnvSettings


class TelegramConfig(EnvSettings, env_prefix="TELEGRAM_"):
    """Конфигурация Telegram бота."""
    
    bot_token: Optional[SecretStr] = None
    locales: StringList = ["en"]
    drop_pending_updates: bool = True
    use_webhook: bool = False
    reset_webhook: bool = False
    webhook_path: str = "/webhook"
    webhook_secret: SecretStr = SecretStr("")
