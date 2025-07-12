"""
Действия для работы с уведомлениями в админ-панели.
"""

from fastapi import Request
from sqlalchemy.future import select
from sqlalchemy import update
from datetime import datetime

from app.models.sql.notification import Notification
from app.models.sql.user import User
from app.admin.utils import is_user_blocked_error
from app.utils.logging import admin as logger


class NotificationActions:
    """Класс для выполнения действий с уведомлениями."""
    
    @staticmethod
    async def preview_notification(request: Request, pks: list) -> str:
        """Показывает предпросмотр уведомления."""
        if not pks:
            return "Не выбрано ни одного уведомления."
        
        try:
            pk = int(pks[0])
        except (ValueError, TypeError):
            return f"Неверный ID уведомления: {pks[0]}"
        
        # Получаем движок из состояния приложения
        engine = request.app.state.engine
        
        async with engine.begin() as conn:
            stmt = select(*Notification.__table__.c).filter_by(id=pk)
            result = await conn.execute(stmt)
            row = result.first()
            
            if row:
                notification = Notification(**row._asdict())
            else:
                notification = None
            
            if not notification or not hasattr(notification, 'id'):
                return f"Ошибка: не удалось получить объект уведомления с ID {pk}"
            
            preview = f"""
            <div style="font-family: Arial, sans-serif; padding: 20px;">
                <h3>Предпросмотр уведомления #{notification.id}</h3>
                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0;">
                    <strong>Текст:</strong><br>
                    {notification.text}
                </div>
                {f'<div style="margin: 10px 0;"><strong>Комментарий:</strong><br>{notification.comment}</div>' if notification.comment else ''}
                <div style="margin: 10px 0;">
                    <strong>Статус:</strong> {notification.status or 'pending'}<br>
                    <strong>Создано:</strong> {notification.created_at.strftime('%d.%m.%Y %H:%M:%S') if notification.created_at else 'N/A'}
                </div>
            </div>
            """
            
            return preview
    
    @staticmethod
    async def send_notification(request: Request, pks: list) -> str:
        """Отправляет уведомление всем активным пользователям."""
        try:
            notification_ids = []
            for pk in pks:
                try:
                    notification_ids.append(int(pk))
                except (ValueError, TypeError):
                    return f"Неверный ID уведомления: {pk}"
            
            results = []
            session_pool = request.app.state.session_pool
            bot = request.app.state.bot
            
            async with session_pool() as session:
                for pk in notification_ids:
                    # Получаем уведомление из базы
                    response = await session.execute(
                        select(Notification).filter_by(id=pk)
                    )
                    notification = response.scalar_one_or_none()
                    
                    if not notification:
                        results.append(f"❌ Уведомление {pk}: Уведомление не найдено")
                        continue
                    
                    try:
                        # Получаем всех активных пользователей
                        users_response = await session.execute(
                            select(User).filter(User.blocked_at.is_(None))
                        )
                        users = users_response.scalars().all()
                        
                        if not users:
                            results.append(f"❌ Уведомление {pk}: Нет активных пользователей")
                            continue
                        
                        # Отправляем уведомление каждому пользователю
                        sent_count = 0
                        error_count = 0
                        blocked_users = []
                        
                        for user in users:
                            try:
                                await bot.send_message(
                                    chat_id=user.id,
                                    text=notification.text
                                )
                                sent_count += 1
                            except Exception as e:
                                error_count += 1
                                error_message = str(e)
                                
                                # Проверяем, заблокировал ли пользователь бота
                                if is_user_blocked_error(error_message):
                                    # Блокируем пользователя
                                    try:
                                        await session.execute(
                                            update(User)
                                            .where(User.id == user.id)
                                            .values(
                                                blocked_at=datetime.utcnow(),
                                                status="blocked"
                                            )
                                        )
                                        blocked_users.append(user.id)
                                        logger.info(f"Пользователь {user.id} заблокирован (заблокировал бота)")
                                    except Exception as block_error:
                                        logger.error(f"Ошибка блокировки пользователя {user.id}: {block_error}")
                                else:
                                    logger.error(f"Ошибка отправки уведомления {pk} пользователю {user.id}: {e}")
                        
                        # Обновляем статус уведомления
                        error_info = []
                        if error_count > 0:
                            error_info.append(f"Ошибок: {error_count}")
                        if blocked_users:
                            error_info.append(f"Заблокировано пользователей: {len(blocked_users)}")
                        
                        await session.execute(
                            update(Notification)
                            .where(Notification.id == pk)
                            .values(
                                status="sent",
                                sent_at=datetime.utcnow(),
                                error="; ".join(error_info) if error_info else None
                            )
                        )
                        await session.commit()
                        
                        result_message = f"✅ Уведомление {pk}: {sent_count} отправлено, {error_count} ошибок"
                        if blocked_users:
                            result_message += f", {len(blocked_users)} пользователей заблокировано"
                        results.append(result_message)
                        
                    except Exception as e:
                        # Обновляем статус уведомления с ошибкой
                        await session.execute(
                            update(Notification)
                            .where(Notification.id == pk)
                            .values(
                                status="error",
                                error=str(e)
                            )
                        )
                        await session.commit()
                        
                        results.append(f"❌ Уведомление {pk}: Ошибка отправки - {str(e)}")
            
            return "<br>".join(results)
        except Exception as e:
            return f"Ошибка при отправке: {str(e)}" 