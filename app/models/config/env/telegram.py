from pydantic import SecretStr

from app.models.config.env.base import EnvSettings
from app.utils.custom_types import StringList


class TelegramConfig(EnvSettings, env_prefix="TELEGRAM_"):
    bot_token: SecretStr
    locales: StringList
    drop_pending_updates: bool
    use_webhook: bool
    reset_webhook: bool
    webhook_path: str
    webhook_secret: SecretStr
