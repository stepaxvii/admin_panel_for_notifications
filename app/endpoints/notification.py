from fastapi import APIRouter, Depends, status

from app.factory.app_config import create_app_config
from app.factory.redis import create_redis
from app.factory.session_pool import create_session_pool
from app.models.dto.notification import NotificationCreate, NotificationUpdate
from app.services.crud.notification import NotificationService


def get_session_pool():
    return create_session_pool(config=create_app_config())


def get_redis():
    return create_redis(config=create_app_config())


def get_config():
    return create_app_config()


def get_notification_service(
    session_pool=Depends(get_session_pool),
    redis=Depends(get_redis),
    config=Depends(get_config),
):
    return NotificationService(session_pool=session_pool, redis=redis, config=config)


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", status_code=status.HTTP_200_OK)
async def list_notifications(service: NotificationService = Depends(get_notification_service)):
    return await service.list_all()


@router.get("/{notification_id}", status_code=status.HTTP_200_OK)
async def get_notification(
    notification_id: int, service: NotificationService = Depends(get_notification_service)
):
    return await service.get(notification_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification: NotificationCreate,
    service: NotificationService = Depends(get_notification_service),
):
    return await service.create(**notification.model_dump())


@router.put("/{notification_id}", status_code=status.HTTP_200_OK)
async def update_notification(
    notification_id: int,
    notification: NotificationUpdate,
    service: NotificationService = Depends(get_notification_service),
):
    return await service.update(notification_id, **notification.model_dump())


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int, service: NotificationService = Depends(get_notification_service)
):
    return await service.delete(notification_id)
