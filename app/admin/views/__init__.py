"""
Views для админ-панели.

Содержит представления моделей для Starlette Admin.
"""

from .notification_view import NotificationView
from .user_view import UserView

__all__ = ["NotificationView", "UserView"] 