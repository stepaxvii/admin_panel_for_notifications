from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.sql.base import Base
from app.models.sql.mixins import TimestampMixin


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(String(length=4096))
    status: Mapped[Optional[str]] = mapped_column(String(length=255))
    error: Mapped[Optional[str]] = mapped_column(String(length=255))
    sent_at: Mapped[Optional[datetime]] = mapped_column()
    comment: Mapped[Optional[str]] = mapped_column(String(length=255))
