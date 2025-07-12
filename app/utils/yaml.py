"""
Утилиты для работы с YAML файлами.

Предоставляет функции для загрузки и обработки YAML конфигураций.
"""

from pathlib import Path
from typing import Any

import yaml

from app.models.base import PydanticModel


class YAMLSettings(PydanticModel):
    """Базовый класс для настроек из YAML файлов."""

    @classmethod
    def from_yaml(cls, yaml_file: str | Path) -> "YAMLSettings":
        """Загрузить настройки из YAML файла."""
        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls(**data)
