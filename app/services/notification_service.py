"""
Сервис для асинхронной рассылки уведомлений через Telegram-бота.

Поддерживает очереди, повторные попытки и детальное логирование.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError

from app.models.sql.notification import Notification
from app.models.sql.user import User
from app.services.postgres.context import SQLSessionContext
from app.utils.logging import notifications as logger


class NotificationStatus(Enum):
    """Статусы уведомлений."""
    PENDING = "pending"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"
    RETRY = "retry"


class UserStatus(Enum):
    """Статусы пользователей."""
    ACTIVE = "active"
    BLOCKED = "blocked"
    INACTIVE = "inactive"
    DELETED = "deleted"


@dataclass
class NotificationTask:
    """Задача отправки уведомления."""
    notification_id: int
    user_id: int
    message: str
    retry_count: int = 0
    max_retries: int = 3
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class NotificationQueue:
    """Очередь для асинхронной отправки уведомлений."""
    
    def __init__(self, max_concurrent: int = 10, batch_size: int = 50):
        self.max_concurrent = max_concurrent
        self.batch_size = batch_size
        self.queue: asyncio.Queue = asyncio.Queue()
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.is_running = False
        self.workers: List[asyncio.Task] = []
        
    async def start(self, send_notification_func):
        """Запускает обработчики очереди."""
        if self.is_running:
            return
            
        self.is_running = True
        logger.info(f"Запуск очереди уведомлений с {self.max_concurrent} обработчиками")
        
        for i in range(self.max_concurrent):
            worker = asyncio.create_task(self._worker(f"worker-{i}", send_notification_func))
            self.workers.append(worker)
    
    async def stop(self):
        """Останавливает обработчики очереди."""
        if not self.is_running:
            return
            
        self.is_running = False
        logger.info("Остановка очереди уведомлений")
        
        await self.queue.join()
        
        for worker in self.workers:
            worker.cancel()
        
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
    
    async def add_task(self, task: NotificationTask):
        """Добавляет задачу в очередь."""
        await self.queue.put(task)
        logger.debug(f"Добавлена задача отправки уведомления {task.notification_id} пользователю {task.user_id}")
    
    async def _worker(self, worker_name: str, send_notification_func):
        """Обработчик задач."""
        logger.info(f"Запущен обработчик {worker_name}")
        
        while self.is_running:
            try:
                task = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                
                async with self.semaphore:
                    await self._process_task(task, worker_name, send_notification_func)
                    
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Ошибка в обработчике {worker_name}: {e}")
        
        logger.info(f"Остановлен обработчик {worker_name}")
    
    async def _process_task(self, task: NotificationTask, worker_name: str, send_notification_func):
        """Обрабатывает одну задачу."""
        try:
            logger.debug(f"{worker_name}: Обработка задачи {task.notification_id} -> {task.user_id}")
            
            success = await send_notification_func(task)
            
            if success:
                logger.info(f"{worker_name}: Успешно отправлено уведомление {task.notification_id} пользователю {task.user_id}")
            else:
                logger.warning(f"{worker_name}: Не удалось отправить уведомление {task.notification_id} пользователю {task.user_id}")
                
                if task.retry_count < task.max_retries:
                    task.retry_count += 1
                    await asyncio.sleep(2 ** task.retry_count)
                    await self.add_task(task)
                    logger.info(f"{worker_name}: Повторная попытка {task.retry_count} для уведомления {task.notification_id}")
                else:
                    logger.error(f"{worker_name}: Исчерпаны попытки для уведомления {task.notification_id}")
                    
        except Exception as e:
            logger.error(f"{worker_name}: Ошибка обработки задачи {task.notification_id}: {e}")
        finally:
            self.queue.task_done()


class NotificationService:
    """Сервис для асинхронной рассылки уведомлений через Telegram-бота."""
    
    def __init__(self, bot: Bot, session_pool):
        self.bot = bot
        self.session_pool = session_pool
        self.queue = NotificationQueue(max_concurrent=10, batch_size=50)
        self._queue_started = False

    async def _handle_telegram_error(self, error: TelegramAPIError, user_id: int) -> Dict[str, Any]:
        """Обрабатывает ошибки Telegram API и возвращает информацию о типе ошибки."""
        error_code = getattr(error, 'code', None)
        error_description = str(error)
        
        # Ошибки блокировки бота
        if isinstance(error, TelegramForbiddenError) or error_code == 403:
            logger.warning(f"Пользователь {user_id} заблокировал бота")
            return {
                "type": "user_blocked",
                "should_retry": False,
                "update_user_status": UserStatus.BLOCKED.value,
                "message": "Пользователь заблокировал бота"
            }
        
        # Ошибки несуществующего чата
        elif error_code == 400 and "chat not found" in error_description.lower():
            logger.warning(f"Чат с пользователем {user_id} не найден")
            return {
                "type": "chat_not_found",
                "should_retry": False,
                "update_user_status": UserStatus.DELETED.value,
                "message": "Чат не найден"
            }
        
        # Ошибки удаленного пользователя
        elif error_code == 400 and "user is deactivated" in error_description.lower():
            logger.warning(f"Пользователь {user_id} деактивирован")
            return {
                "type": "user_deactivated",
                "should_retry": False,
                "update_user_status": UserStatus.INACTIVE.value,
                "message": "Пользователь деактивирован"
            }
        
        # Ошибки ограничений (спам, флуд)
        elif error_code == 429:
            logger.warning(f"Превышен лимит отправки для пользователя {user_id}")
            return {
                "type": "rate_limit",
                "should_retry": True,
                "update_user_status": None,
                "message": "Превышен лимит отправки"
            }
        
        # Ошибки сервера Telegram
        elif error_code in [500, 502, 503, 504]:
            logger.warning(f"Ошибка сервера Telegram для пользователя {user_id}: {error_code}")
            return {
                "type": "server_error",
                "should_retry": True,
                "update_user_status": None,
                "message": f"Ошибка сервера Telegram: {error_code}"
            }
        
        # Другие ошибки
        else:
            logger.error(f"Неизвестная ошибка Telegram для пользователя {user_id}: {error_code} - {error_description}")
            return {
                "type": "unknown_error",
                "should_retry": True,
                "update_user_status": None,
                "message": f"Неизвестная ошибка: {error_description}"
            }

    async def _update_user_status(self, user_id: int, status: str) -> None:
        """Обновляет статус пользователя в базе данных."""
        try:
            async with SQLSessionContext(self.session_pool) as (repository, uow):
                # Обновляем статус пользователя через репозиторий
                updated_user = await repository.users.update_user_status(user_id, status)
                if updated_user:
                    logger.info(f"Обновлен статус пользователя {user_id} на {status}")
                else:
                    logger.warning(f"Пользователь {user_id} не найден для обновления статуса")
        except Exception as e:
            logger.error(f"Ошибка обновления статуса пользователя {user_id}: {e}")

    async def _send_notification(self, task: NotificationTask) -> bool:
        """Отправляет уведомление через бота."""
        try:
            await self.bot.send_message(
                chat_id=task.user_id,
                text=task.message,
                parse_mode="HTML"
            )
            logger.info(f"Уведомление отправлено пользователю {task.user_id}")
            return True
            
        except TelegramAPIError as e:
            error_info = await self._handle_telegram_error(e, task.user_id)
            
            # Обновляем статус пользователя если нужно
            if error_info["update_user_status"]:
                await self._update_user_status(task.user_id, error_info["update_user_status"])
            
            # Логируем детальную информацию об ошибке
            logger.error(
                f"Ошибка отправки уведомления пользователю {task.user_id}: "
                f"{error_info['type']} - {error_info['message']}"
            )
            
            # Возвращаем False для ошибок, которые не нужно повторять
            return error_info["should_retry"]
            
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке уведомления пользователю {task.user_id}: {e}")
            return False
    
    async def _ensure_queue_running(self):
        """Убеждается, что очередь запущена."""
        if not self._queue_started:
            await self.queue.start(self._send_notification)
            self._queue_started = True
    
    async def send_notification_to_user(self, user_id: int, message: str) -> Dict[str, Any]:
        """Отправляет уведомление одному пользователю с детальной обработкой ошибок."""
        try:
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode="HTML"
            )
            logger.info(f"Уведомление отправлено пользователю {user_id}")
            return {
                "success": True,
                "user_id": user_id,
                "error_type": None,
                "message": "Уведомление отправлено"
            }
            
        except TelegramAPIError as e:
            error_info = await self._handle_telegram_error(e, user_id)
            
            # Обновляем статус пользователя если нужно
            if error_info["update_user_status"]:
                await self._update_user_status(user_id, error_info["update_user_status"])
            
            return {
                "success": False,
                "user_id": user_id,
                "error_type": error_info["type"],
                "message": error_info["message"],
                "should_retry": error_info["should_retry"]
            }
            
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке уведомления пользователю {user_id}: {e}")
            return {
                "success": False,
                "user_id": user_id,
                "error_type": "unexpected_error",
                "message": str(e),
                "should_retry": True
            }

    async def send_bulk_notification(self, notification_id: int) -> Dict[str, Any]:
        """Массовая рассылка уведомления всем активным пользователям."""
        start_time = datetime.utcnow()
        
        try:
            await self._ensure_queue_running()
            
            async with SQLSessionContext(self.session_pool) as (repository, uow):
                notification = await repository._get(Notification, Notification.id == notification_id)
                if not notification:
                    return {
                        "success": False, 
                        "error": f"Уведомление с ID {notification_id} не найдено"
                    }
                
                await repository._update(
                    Notification, 
                    [Notification.id == notification_id], 
                    status=NotificationStatus.SENDING.value
                )
                
                users = await repository.users.get_active_users()
                if not users:
                    await repository._update(
                        Notification, 
                        [Notification.id == notification_id], 
                        status=NotificationStatus.SENT.value,
                        sent_at=datetime.utcnow()
                    )
                    return {
                        "success": True, 
                        "message": "Нет активных пользователей для рассылки", 
                        "total": 0, 
                        "sent": 0, 
                        "failed": 0
                    }
                
                # Отправляем уведомления напрямую для получения реальных результатов
                sent_count = 0
                failed_count = 0
                failed_users = []
                
                for user in users:
                    result = await self.send_notification_to_user(user.id, notification.text)
                    
                    if result["success"]:
                        sent_count += 1
                    else:
                        failed_count += 1
                        failed_users.append({
                            "user_id": user.id,
                            "error_type": result["error_type"],
                            "message": result["message"]
                        })
                        
                        # Логируем детали ошибки
                        logger.warning(
                            f"Не удалось отправить уведомление {notification_id} пользователю {user.id}: "
                            f"{result['error_type']} - {result['message']}"
                        )
                
                end_time = datetime.utcnow()
                duration = (end_time - start_time).total_seconds()
                
                # Определяем финальный статус уведомления
                if failed_count == 0:
                    status = NotificationStatus.SENT.value
                    error_msg = None
                elif sent_count == 0:
                    status = NotificationStatus.FAILED.value
                    error_msg = f"Не удалось отправить ни одному пользователю из {len(users)}"
                else:
                    status = NotificationStatus.SENT.value  # Частично успешно
                    error_msg = f"Отправлено {sent_count} из {len(users)}, не удалось отправить {failed_count}"
                
                await repository._update(
                    Notification, 
                    [Notification.id == notification_id], 
                    status=status,
                    error=error_msg,
                    sent_at=end_time
                )
                
                logger.info(
                    f"Рассылка уведомления {notification_id} завершена: "
                    f"{sent_count} отправлено, {failed_count} ошибок за {duration:.2f}s"
                )
                
                if failed_users:
                    logger.info(f"Детали ошибок для уведомления {notification_id}: {failed_users}")
                
                return {
                    "success": True,
                    "message": f"Рассылка завершена за {duration:.2f} секунд",
                    "total": len(users),
                    "sent": sent_count,
                    "failed": failed_count,
                    "duration": duration,
                    "failed_users": failed_users
                }
                
        except Exception as e:
            logger.error(f"Ошибка при массовой рассылке уведомления {notification_id}: {e}")
            
            try:
                async with SQLSessionContext(self.session_pool) as (repository, uow):
                    await repository._update(
                        Notification, 
                        [Notification.id == notification_id], 
                        status=NotificationStatus.FAILED.value,
                        error=str(e)
                    )
            except Exception as update_error:
                logger.error(f"Ошибка обновления статуса уведомления {notification_id}: {update_error}")
            
            return {
                "success": False, 
                "error": f"Ошибка при рассылке: {str(e)}"
            }

    async def get_notification_stats(self, notification_id: int) -> Optional[Dict[str, Any]]:
        """Получить статистику по уведомлению."""
        try:
            async with SQLSessionContext(self.session_pool) as (repository, uow):
                notification = await repository._get(Notification, Notification.id == notification_id)
                if not notification:
                    return None
                
                return {
                    "id": notification.id,
                    "text": notification.text,
                    "status": notification.status,
                    "error": notification.error,
                    "created_at": notification.created_at,
                    "sent_at": notification.sent_at,
                    "updated_at": notification.updated_at
                }
        except Exception as e:
            logger.error(f"Ошибка при получении статистики уведомления {notification_id}: {e}")
            return None
    
    async def cleanup(self):
        """Очистка ресурсов."""
        if self._queue_started:
            await self.queue.stop()
            self._queue_started = False 