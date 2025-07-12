"""
API endpoints для управления уведомлениями.

Предоставляет интерфейс для отправки уведомлений и получения статистики.
"""

import asyncio
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks, Request, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime, timedelta

from app.models.sql.notification import Notification
from app.models.sql.user import User
from app.services.notification_service import NotificationService


class SendNotificationRequest(BaseModel):
    """Запрос на отправку уведомления."""
    notification_id: int


class SendNotificationResponse(BaseModel):
    """Ответ на отправку уведомления."""
    success: bool
    message: str
    notification_id: int
    sent_count: int = 0
    error_count: int = 0
    total_users: int = 0


router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.post("/send")
async def send_notification(
    data: SendNotificationRequest,
    req: Request
) -> Dict[str, Any]:
    """Отправляет уведомление всем активным пользователям."""
    try:
        bot = req.app.state.bot
        session_pool = req.app.state.session_pool
        
        notification_service = NotificationService(bot, session_pool)
        result = await notification_service.send_bulk_notification(data.notification_id)
        
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Неизвестная ошибка"))
        
        return {
            "message": result.get("message", "Уведомление отправлено"),
            "notification_id": data.notification_id,
            "sent_count": result.get("sent", 0),
            "error_count": result.get("failed", 0),
            "total_users": result.get("total", 0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка отправки: {str(e)}")


@router.get("/{notification_id}/status")
async def get_notification_status(
    notification_id: int,
    req: Request
) -> Dict[str, Any]:
    """Получает детальный статус конкретного уведомления."""
    try:
        session_pool = req.app.state.session_pool
        
        async with session_pool() as session:
            result = await session.execute(
                select(Notification).where(Notification.id == notification_id)
            )
            notification = result.scalar_one_or_none()
            
            if not notification:
                raise HTTPException(status_code=404, detail="Уведомление не найдено")
            
            return {
                "id": notification.id,
                "text": notification.text,
                "status": notification.status,
                "error": notification.error,
                "created_at": notification.created_at.isoformat() if notification.created_at else None,
                "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
                "updated_at": notification.updated_at.isoformat() if notification.updated_at else None
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения статуса: {str(e)}")


@router.get("/recent")
async def get_recent_notifications(
    req: Request,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Получает последние уведомления."""
    try:
        session_pool = req.app.state.session_pool
        
        async with session_pool() as session:
            result = await session.execute(
                select(Notification)
                .order_by(Notification.created_at.desc())
                .limit(limit)
            )
            
            notifications = result.scalars().all()
            
            return [
                {
                    "id": n.id,
                    "text": n.text[:100] + "..." if len(n.text) > 100 else n.text,
                    "status": n.status,
                    "created_at": n.created_at.isoformat() if n.created_at else None,
                    "sent_at": n.sent_at.isoformat() if n.sent_at else None
                }
                for n in notifications
            ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения уведомлений: {str(e)}")


@router.post("/retry/{notification_id}")
async def retry_notification(
    notification_id: int,
    req: Request
) -> Dict[str, Any]:
    """Повторно отправляет неудачное уведомление."""
    try:
        bot = req.app.state.bot
        session_pool = req.app.state.session_pool
        
        async with session_pool() as session:
            result = await session.execute(
                select(Notification).where(Notification.id == notification_id)
            )
            notification = result.scalar_one_or_none()
            
            if not notification:
                raise HTTPException(status_code=404, detail="Уведомление не найдено")
            
            if notification.status == "sent":
                return {"message": "Уведомление уже отправлено", "status": "already_sent"}
            
            notification.status = "pending"
            notification.error = None
            notification.sent_at = None
            await session.commit()
        
        notification_service = NotificationService(bot, session_pool)
        result = await notification_service.send_bulk_notification(notification_id)
        
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Неизвестная ошибка"))
        
        return {
            "message": "Уведомление повторно отправлено",
            "notification_id": notification_id,
            "sent_count": result.get("sent", 0),
            "error_count": result.get("failed", 0),
            "total_users": result.get("total", 0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка повторной отправки: {str(e)}") 