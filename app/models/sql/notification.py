"""
Модель уведомлений для базы данных.

Представляет уведомления, отправляемые пользователям бота.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import TimestampMixin


class Notification(Base, TimestampMixin):
    """Модель уведомления в базе данных."""
    
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(String(length=4096))
    status: Mapped[str] = mapped_column(String(length=32), default="draft")
    error: Mapped[Optional[str]] = mapped_column(String(length=1024), nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(String(length=1024), nullable=True) 