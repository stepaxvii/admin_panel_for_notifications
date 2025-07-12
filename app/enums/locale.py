from __future__ import annotations

from enum import auto

from aiogram_i18n import LazyProxy


# noinspection PyEnum
class Locale(str, LazyProxy):
    EN = auto()  # English
