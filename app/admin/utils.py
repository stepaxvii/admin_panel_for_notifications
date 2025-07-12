"""
Утилиты для админ-панели.

Содержит вспомогательные функции для работы админ-панели.
"""

import subprocess
import sys
from app.utils.logging import admin as logger


def run_alembic_upgrade() -> None:
    """Применяет миграции Alembic к базе данных."""
    try:
        logger.info("Применение миграций Alembic...")
        result = subprocess.run(["alembic", "upgrade", "head"], check=True, capture_output=True, text=True)
        logger.info(f"[alembic stdout]\n{result.stdout}")
        if result.stderr:
            logger.warning(f"[alembic stderr]\n{result.stderr}")
    except subprocess.CalledProcessError as e:
        logger.error(f"[alembic ERROR] Код возврата: {e.returncode}")
        logger.error(f"[alembic stdout]\n{e.stdout}")
        logger.error(f"[alembic stderr]\n{e.stderr}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Ошибка применения миграций: {e}")
        sys.exit(1)


def is_user_blocked_error(error_message: str) -> bool:
    """Проверяет, является ли ошибка результатом блокировки бота пользователем."""
    error_lower = error_message.lower()
    blocked_keywords = [
        "bot was blocked by the user",
        "bot was stopped by the user", 
        "user is deactivated",
        "chat not found",
        "user not found",
        "forbidden: bot was blocked by the user",
        "forbidden: user is deactivated"
    ]
    return any(keyword in error_lower for keyword in blocked_keywords) 