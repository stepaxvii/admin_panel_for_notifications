from typing import Any, Optional, cast, List

from sqlalchemy import select
from sqlalchemy.sql.functions import count

from app.models.sql import User
from app.services.postgres.repositories.base import BaseRepository


# noinspection PyTypeChecker
class UsersRepository(BaseRepository):
    async def get(self, user_id: int) -> Optional[User]:
        return await self._get(User, User.id == user_id)

    async def update(self, user_id: int, **data: Any) -> Optional[User]:
        return await self._update(
            model=User,
            conditions=[User.id == user_id],
            load_result=True,
            **data,
        )

    async def count(self) -> int:
        return cast(int, await self.session.scalar(select(count(User.id))))

    async def get_active_users(self) -> List[User]:
        """Получает всех активных пользователей для рассылки (не заблокированных и активных)"""
        result = await self.session.execute(
            select(User).where(
                User.blocked_at.is_(None),
                User.status == "active"
            )
        )
        return list(result.scalars().all())

    async def get_users_by_status(self, status: str) -> List[User]:
        """Получает пользователей по статусу."""
        result = await self.session.execute(
            select(User).where(User.status == status)
        )
        return list(result.scalars().all())

    async def update_user_status(self, user_id: int, status: str) -> Optional[User]:
        """Обновляет статус пользователя."""
        return await self._update(
            model=User,
            conditions=[User.id == user_id],
            load_result=True,
            status=status
        )

    async def get_blocked_users(self) -> List[User]:
        """Получает заблокированных пользователей."""
        return await self.get_users_by_status("blocked")

    async def get_inactive_users(self) -> List[User]:
        """Получает неактивных пользователей."""
        return await self.get_users_by_status("inactive")

    async def get_deleted_users(self) -> List[User]:
        """Получает удаленных пользователей."""
        return await self.get_users_by_status("deleted")
