"""
Представление модели уведомлений в админ-панели.
"""

from fastapi import Request
from starlette_admin.contrib.sqla import ModelView
from starlette_admin import action
from sqlalchemy.future import select
from sqlalchemy import update
from datetime import datetime

from app.models.sql.notification import Notification
from app.admin.actions.notification_actions import NotificationActions


class NotificationView(ModelView):
    """Представление модели уведомлений в админ-панели."""
    
    name = "Уведомление"
    name_plural = "Уведомления"
    icon = "fa fa-bell"
    
    can_export = False
    can_set_page_size = False
    page_size = 20
    
    column_list = ["id", "text", "comment", "status", "error", "created_at", "sent_at"]
    column_searchable_list = ["text", "comment"]
    column_sortable_list = ["id", "status", "created_at", "sent_at"]
    
    column_labels = {
        "id": "ID",
        "text": "Текст",
        "comment": "Комментарий",
        "status": "Статус",
        "error": "Ошибка",
        "created_at": "Создано",
        "sent_at": "Отправлено",
    }
    
    form_labels = {
        "text": "Текст уведомления",
        "comment": "Комментарий (необязательно)",
    }
    
    form_include_pk = False
    form_excluded_columns = ["id", "status", "error", "sent_at", "created_at", "updated_at"]
    form_columns = ["text", "comment"]
    
    form_widget_args = {
        "text": {"rows": 5, "placeholder": "Введите текст уведомления..."},
        "comment": {"rows": 3, "placeholder": "Введите комментарий (необязательно)..."}
    }
    
    def get_form_fields(self, request: Request) -> list:
        """Возвращает поля для формы."""
        return ["text", "comment"]
    
    def get_create_form_fields(self, request: Request) -> list:
        """Возвращает поля для формы создания."""
        return ["text", "comment"]
    
    def get_edit_form_fields(self, request: Request) -> list:
        """Возвращает поля для формы редактирования."""
        return ["text", "comment"]
    
    @action(
        name="preview_notification",
        text="Предпросмотр",
        confirmation=None,
        submit_btn_text="Закрыть",
        submit_btn_class="btn-secondary",
    )
    async def preview_notification_action(self, request: Request, pks: list) -> str:
        """Показывает предпросмотр уведомления."""
        return await NotificationActions.preview_notification(request, pks)
    
    @action(
        name="send_notification",
        text="Отправить уведомление",
        confirmation="Вы уверены, что хотите отправить это уведомление всем пользователям?",
        submit_btn_text="Да, отправить",
        submit_btn_class="btn-primary",
    )
    async def send_notification_action(self, request: Request, pks: list) -> str:
        """Отправляет уведомление всем активным пользователям."""
        return await NotificationActions.send_notification(request, pks) 