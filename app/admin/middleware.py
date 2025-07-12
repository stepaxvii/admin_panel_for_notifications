"""
Middleware для админ-панели.

Содержит middleware функции для обработки запросов.
"""

import time
from fastapi import Request
from app.utils.logging import admin as logger


async def performance_middleware(request: Request, call_next):
    """Middleware для мониторинга производительности запросов."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    if process_time > 1.0:
        logger.warning(f"МЕДЛЕННЫЙ ЗАПРОС: {request.url.path} - {process_time:.2f}с")
    else:
        logger.debug(f"ПРОИЗВОДИТЕЛЬНОСТЬ: {request.url.path} - {process_time:.2f}с")
    
    return response 