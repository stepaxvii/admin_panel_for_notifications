"""
Миксин для добавления временных меток к моделям.

Автоматически добавляет поля created_at и updated_at с UTC временем.
"""

from datetime import datetime
from typing import Any, Final

from sqlalchemy import Function, func
from sqlalchemy.orm import Mapped, mapped_column

NowFunc: Final[Function[Any]] = func.timezone("UTC", func.now())


class TimestampMixin:
    """Миксин для автоматического управления временными метками."""
    
    created_at: Mapped[datetime] = mapped_column(server_default=NowFunc)
    updated_at: Mapped[datetime] = mapped_column(server_default=NowFunc, server_onupdate=NowFunc)
