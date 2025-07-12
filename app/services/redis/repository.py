from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Final, Optional, TypeVar, cast

from pydantic import BaseModel, TypeAdapter
from redis.asyncio import Redis
from redis.typing import ExpiryT

from app.services.redis.keys import WebhookLockKey
from app.utils import mjson
from app.utils.key_builder import StorageKey
from app.utils.logging import redis as logger

if TYPE_CHECKING:
    from app.models.config import AppConfig

T = TypeVar("T", bound=Any)

TX_QUEUE_KEY: Final[str] = "tx_queue"
MASS_SEND_QUEUE_KEY: Final[str] = "mass_send_queue"


class RedisRepository:
    client: Redis
    config: AppConfig

    def __init__(self, client: Redis, config: AppConfig) -> None:
        self.client = client
        self.config = config
        logger.info("Redis репозиторий инициализирован")

    async def get(
        self,
        key: StorageKey,
        validator: type[T],
        default: Optional[T] = None,
    ) -> Optional[T]:
        value: Optional[Any] = await self.client.get(key.pack())
        if value is None:
            logger.debug(f"Ключ не найден: {key.pack()}")
            return default
        value = mjson.decode(value)
        return TypeAdapter[T](validator).validate_python(value)

    async def set(self, key: StorageKey, value: Any, ex: Optional[ExpiryT] = None) -> None:
        if isinstance(value, BaseModel):
            value = value.model_dump(exclude_defaults=True)
        await self.client.set(name=key.pack(), value=mjson.encode(value), ex=ex)
        logger.debug(f"Установлен ключ: {key.pack()}")

    async def exists(self, key: StorageKey) -> bool:
        return cast(bool, await self.client.exists(key.pack()))

    async def delete(self, key: StorageKey) -> None:
        await self.client.delete(key.pack())
        logger.debug(f"Удален ключ: {key.pack()}")

    async def close(self) -> None:
        await self.client.aclose(close_connection_pool=True)
        logger.info("Redis соединение закрыто")

    async def is_webhook_set(self, bot_id: int, webhook_hash: str) -> bool:
        key: WebhookLockKey = WebhookLockKey(
            bot_id=bot_id,
            webhook_hash=webhook_hash,
        )
        return await self.exists(key=key)

    async def set_webhook(self, bot_id: int, webhook_hash: str) -> None:
        key: WebhookLockKey = WebhookLockKey(
            bot_id=bot_id,
            webhook_hash=webhook_hash,
        )
        await self.set(key=key, value=None)
        logger.info(f"Установлен webhook для бота {bot_id}")

    async def clear_webhooks(self, bot_id: int) -> None:
        key: WebhookLockKey = WebhookLockKey(bot_id=bot_id, webhook_hash="*")
        keys: list[bytes] = await self.client.keys(key.pack())
        if not keys:
            return
        await self.client.delete(*keys)
        logger.info(f"Очищены webhook'и для бота {bot_id}")

    # ===== Очередь массовой рассылки =====
    async def enqueue_mass_send(self, notification: dict) -> None:
        """Добавить задачу массовой рассылки в очередь."""
        await self.client.rpush(MASS_SEND_QUEUE_KEY, mjson.encode(notification))  # type: ignore
        logger.info(f"Добавлена задача в очередь рассылки: {notification.get('notification_id', 'unknown')}")

    async def dequeue_mass_send(self) -> Optional[dict]:
        """Извлечь задачу массовой рассылки из очереди."""
        value = await self.client.lpop(MASS_SEND_QUEUE_KEY)  # type: ignore
        if value is None:
            logger.debug("Очередь рассылки пуста")
            return None
        task = mjson.decode(value)
        logger.debug(f"Извлечена задача из очереди: {task.get('notification_id', 'unknown')}")
        return task
