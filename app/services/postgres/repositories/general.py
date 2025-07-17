from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.postgres.repositories.base import BaseRepository
from app.services.postgres.repositories.users import UsersRepository


class Repository(BaseRepository):
    users: UsersRepository

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session)
        self.users = UsersRepository(session=session)
