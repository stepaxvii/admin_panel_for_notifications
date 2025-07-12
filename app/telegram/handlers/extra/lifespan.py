from __future__ import annotations

import logging
from typing import Final

from aiogram import Bot, Router
from aiogram.types import BotCommand

from app.models.config import AppConfig
from app.runners.lifespan import close_sessions

logger: Final[logging.Logger] = logging.getLogger(name=__name__)
router: Final[Router] = Router(name=__name__)
router.shutdown.register(close_sessions)


async def setup_commands(bot: Bot, app_config: AppConfig) -> None:
    """Установить команды бота."""
    commands = [
        BotCommand(command="start", description="Главное меню"),
    ]
    await bot.set_my_commands(commands)
