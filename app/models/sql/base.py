"""
Базовая модель SQLAlchemy для всех таблиц.

Определяет общие настройки и типы данных для всех моделей.
"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, SmallInteger, String
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from sqlalchemy.orm import DeclarativeBase, registry

from app.utils.custom_types import DictStrAny, Int16, Int32, Int64


class Base(DeclarativeBase):
    """Базовая модель для всех таблиц базы данных."""
    
    registry = registry(
        type_annotation_map={
            Int16: SmallInteger(),
            Int32: Integer(),
            Int64: BigInteger(),
            DictStrAny: JSON(),
            list[str]: ARRAY(String()),
            datetime: DateTime(timezone=True),
        }
    )
