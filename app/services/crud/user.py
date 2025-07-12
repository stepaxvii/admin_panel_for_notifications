from __future__ import annotations

from typing import Any, Optional

from aiogram.types import User as AiogramUser
from aiogram_i18n.cores import BaseCore

from app.models.dto.user import UserDto
from app.models.sql import User
from app.services.crud.base import CrudService
from app.services.postgres import SQLSessionContext
from app.services.redis.cache_wrapper import redis_cache
from app.utils.key_builder import build_key

class UserService(CrudService):
    """
    Сервис для работы с пользователями Telegram-бота.
    """
    async def clear_cache(self, user_id: int) -> None:
        """Очистить кэш пользователя по user_id."""
        cache_key: str = build_key("cache", "get_user", user_id=user_id)
        await self.redis.delete(cache_key)

    async def create(self, aiogram_user: AiogramUser, i18n_core: BaseCore[Any]) -> UserDto:
        """
        Создать пользователя в базе данных, если его ещё нет.
        :param aiogram_user: Объект пользователя Telegram
        :param i18n_core: Ядро локализации
        :return: DTO пользователя
        """
        db_user: User = User(
            id=aiogram_user.id,
            name=aiogram_user.full_name,
            language=(
                aiogram_user.language_code
                if aiogram_user.language_code in i18n_core.available_locales
                else "en" # Changed from DEFAULT_LOCALE to "en"
            ),
            language_code=aiogram_user.language_code,
        )
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, uow):
            repository.session.add(db_user)
            await repository.session.commit()
        await self.clear_cache(user_id=aiogram_user.id)
        return db_user.dto()

    @redis_cache(prefix="get_user", ttl=60)
    async def get(self, user_id: int) -> Optional[UserDto]:
        """
        Получить пользователя по user_id из базы данных или кэша.
        :param user_id: Telegram ID пользователя
        :return: DTO пользователя или None
        """
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, uow):
            user = await repository.users.get(user_id=user_id)
            if user is None:
                return None
            return user.dto()

    async def count(self) -> int:
        """Получить количество пользователей в базе."""
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, uow):
            return await repository.users.count()

    async def update(self, user: UserDto, **data: Any) -> Optional[UserDto]:
        """
        Обновить данные пользователя.
        :param user: DTO пользователя
        :param data: Данные для обновления
        :return: Обновленный DTO пользователя или None
        """
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, uow):
            for key, value in data.items():
                setattr(user, key, value)
            await self.clear_cache(user_id=user.id)
            user_db = await repository.users.update(user_id=user.id, **user.model_state)
            if user_db is None:
                return None
            return user_db.dto()

    async def get_or_create(self, aiogram_user: AiogramUser, i18n_core: BaseCore[Any]) -> tuple[UserDto, bool]:
        """
        Получить пользователя из базы данных или создать нового.
        :param aiogram_user: Объект пользователя Telegram
        :param i18n_core: Ядро локализации
        :return: Кортеж (DTO пользователя, был_ли_создан)
        """
        # Сначала пытаемся получить существующего пользователя
        existing_user = await self.get(user_id=aiogram_user.id)
        if existing_user is not None:
            return existing_user, False
        
        # Если пользователя нет, создаем нового
        new_user = await self.create(aiogram_user=aiogram_user, i18n_core=i18n_core)
        return new_user, True
