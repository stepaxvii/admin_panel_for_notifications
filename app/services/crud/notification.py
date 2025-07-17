from typing import Any, List, Optional

from app.const import TIME_1M
from app.models.dto.notification import NotificationDTO
from app.services.crud.base import CrudService
from app.services.postgres import SQLSessionContext
from app.services.redis.cache_wrapper import redis_cache


class NotificationService(CrudService):
    @redis_cache(prefix="get_notification", ttl=TIME_1M)
    async def get(self, notification_id: int) -> Optional[NotificationDTO]:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, uow):
            notification = await uow.notifications.get(notification_id=notification_id)
            return NotificationDTO.model_validate(notification) if notification else None

    @redis_cache(prefix="list_notifications", ttl=TIME_1M)
    async def list_all(self) -> List[NotificationDTO]:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, uow):
            notifications = await uow.notifications.list_all()
            return [NotificationDTO.model_validate(n) for n in notifications]

    async def create(self, **kwargs: Any) -> NotificationDTO:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, uow):
            notification = await uow.notifications.create(**kwargs)
        await self.redis.delete("list_notifications")
        await self.redis.delete(f"get_notification:{notification.id}")
        return NotificationDTO.model_validate(notification)

    async def update(self, notification_id: int, **kwargs: Any) -> Optional[NotificationDTO]:
        update_data = {key: value for key, value in kwargs.items() if value is not None}
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, uow):
            notification = await uow.notifications.update(notification_id, **update_data)
        await self.redis.delete("list_notifications")
        await self.redis.delete(f"get_notification:{notification_id}")
        return NotificationDTO.model_validate(notification) if notification else None

    async def delete(self, notification_id: int) -> bool:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, uow):
            result = await uow.notifications.delete(notification_id)
        await self.redis.delete("list_notifications")
        await self.redis.delete(f"get_notification:{notification_id}")
        return result
