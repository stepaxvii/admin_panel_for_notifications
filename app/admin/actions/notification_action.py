import logging

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.models.sql.notification import Notification
from app.models.sql.user import User

logger = logging.getLogger(__name__)


class NotificationActions:
    @staticmethod
    async def send_notification(request: Request, pks: list[int]):
        session: AsyncSession = request.state.session
        pks = [int(pk) for pk in pks]
        try:
            notifications = await session.execute(
                Notification.__table__.select().where(Notification.id.in_(pks))
            )
            notifications = notifications.fetchall()
            notification_ids = [n.id for n in notifications]
        except Exception as e:
            logger.error(f"Error fetching notifications: {e}")
            raise e
        try:
            users = await session.execute(User.__table__.select())
            users = users.fetchall()
        except Exception as e:
            logger.error(f"Error fetching users: {e}")
        users_ids = [user.id for user in users]
        logger.info(f"Sending notification(s) to {len(users_ids)} users.")
        from app.celery.celery_tasks.notification import send_mass_message
        for notification in notifications:
            logger.info(f"Sending notification {notification.id} with text '{notification.text}' to users: {users_ids}")
            send_mass_message.delay(notification.text, users_ids, notification.id)
        return f"Sent notification {notification_ids}."

    @staticmethod
    async def preview_notification(request: Request, pks: list[int]):
        session: AsyncSession = request.state.session
        pks = [int(pk) for pk in pks]
        try:
            notifications = await session.execute(
                Notification.__table__.select().where(Notification.id.in_(pks))
            )
            notifications = notifications.fetchall()
        except Exception as e:
            logger.error(f"Error fetching notifications: {e}")
            raise e
        previews = []
        for notification in notifications:
            preview = f"""
                <div style="font-family: Arial, sans-serif; padding: 20px;">
                    <h3>Notification Preview #{notification.id}</h3>
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0;">
                        <strong>Text:</strong><br>
                        {notification.text}
                    </div>
                    {f'<div style="margin: 10px 0;"><strong>Comment:</strong><br>{notification.comment}</div>' if notification.comment else ''}
                    <div style="margin: 10px 0;">
                        <strong>Status:</strong> {notification.status or 'pending'}<br>
                        <strong>Create at:</strong> {notification.created_at.strftime('%d.%m.%Y %H:%M:%S') if notification.created_at else 'N/A'}
                    </div>
                </div>
                """
            previews.append(preview)
        return "\n".join(previews)
