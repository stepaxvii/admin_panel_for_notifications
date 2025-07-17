from datetime import datetime
from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.dto.user import UserDto
from app.models.sql.base import Base
from app.models.sql.mixins import TimestampMixin
from app.utils.custom_types import Int64


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[Int64] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    language: Mapped[str] = mapped_column(String(length=2))
    language_code: Mapped[Optional[str]] = mapped_column()
    blocked_at: Mapped[Optional[datetime]] = mapped_column()

    def dto(self) -> UserDto:
        return UserDto.model_validate(self)
