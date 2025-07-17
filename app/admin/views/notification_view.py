from starlette.requests import Request
from starlette_admin.actions import action
from starlette_admin.contrib.sqla import ModelView

from app.admin.actions.notification_action import NotificationActions


class NotificationView(ModelView):
    exclude_fields = ["id", "status", "error", "sent_at", "created_at", "updated_at"]
    exclude_fields_from_create = exclude_fields
    exclude_fields_from_edit = exclude_fields

    @action(
        name="send_notification",
        text="Send notification",
        confirmation="Are you sure you want to send this notification to all users?",
    )
    async def send_notification(self, request: Request, pks: list[int]):
        return await NotificationActions.send_notification(request, pks)

    @action(
        name="preview_notification",
        text="Preview notification",
    )
    async def preview_notification(self, request: Request, pks: list[int]):
        return await NotificationActions.preview_notification(request, pks)
