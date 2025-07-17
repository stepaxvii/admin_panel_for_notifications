from typing import Any, Optional

from app.models.sql.notification import Notification
from app.services.postgres.repositories.base import BaseRepository


class NotificationsRepository(BaseRepository):

    async def create(self, **kwargs: Any) -> Notification:
        notification = Notification(**kwargs)
        self.session.add(notification)
        await self.session.commit()
        await self.session.refresh(notification)
        return notification

    async def list_all(self) -> list[Notification]:
        return await self._get_many(Notification)

    async def get(self, notification_id: int) -> Optional[Notification]:
        return await self._get(Notification, Notification.id == notification_id)

    async def update(self, notification_id: int, **kwargs: Any) -> Optional[Notification]:
        return await self._update(Notification, [Notification.id == notification_id], **kwargs)

    async def delete(self, notification_id: int) -> bool:
        return await self._delete(Notification, Notification.id == notification_id)
