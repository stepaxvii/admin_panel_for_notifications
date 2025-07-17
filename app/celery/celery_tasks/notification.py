import asyncio

from aiogram import Bot
from aiogram.exceptions import AiogramError, TelegramForbiddenError
from celery.utils.log import get_task_logger

from app.celery.celery_app import celery_app
from app.factory import create_app_config
from app.factory.redis import create_redis
from app.factory.session_pool import create_session_pool
from app.models.config.env.telegram import TelegramConfig
from app.models.config import AppConfig
from app.services.crud.notification import NotificationService
from app.utils.time import datetime_now


logger = get_task_logger(__name__)


@celery_app.task
def send_mass_message(text: str, user_ids: list[int], notification_id: int):
    logger.info(f"Starting send_mass_message: notification_id={notification_id}, user_ids={user_ids}")
    success = 0
    blocked = 0
    failed = 0
    try:
        bot_token = TelegramConfig().bot_token.get_secret_value()  # type: ignore
    except Exception as e:
        logger.error(f"Error getting bot token: {e}")
        raise e

    async def send_mass():
        nonlocal success, blocked, failed
        async with Bot(token=bot_token) as bot:
            for user_id in user_ids:
                try:
                    await bot.send_message(user_id, text)
                    success += 1
                except TelegramForbiddenError:
                    logger.warning(f"User {user_id} blocked the bot.")
                    blocked += 1
                except AiogramError as e:
                    logger.error(f"Failed to send message to {user_id}: {e}")
                    failed += 1
                except Exception as e:
                    logger.exception(f"Unexpected error sending message to {user_id}: {e}")
                    failed += 1

    asyncio.run(send_mass())
    config: AppConfig = create_app_config()
    session_pool = create_session_pool(config)
    redis = create_redis(config)
    notification_service = NotificationService(session_pool=session_pool, redis=redis, config=config)
    if success > 0:
        logger.info(f"Attempting to update notification {notification_id} as sent (success={success})")
        result = asyncio.run(notification_service.update(notification_id, sent_at=datetime_now(), status="Send"))
        logger.info(f"Update result for notification {notification_id} (sent): {result}")
    if failed > 0:
        logger.info(f"Attempting to update notification {notification_id} as error (failed={failed})")
        result = asyncio.run(notification_service.update(notification_id, error="Error"))
        logger.info(f"Update result for notification {notification_id} (error): {result}")
    logger.info(
        f"Mass message result: success={success}, blocked={blocked}, failed={failed}, total={len(user_ids)}"
    )
    logger.info(f"Finished send_mass_message: notification_id={notification_id}")
