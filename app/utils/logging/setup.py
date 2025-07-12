"""
Настройка системы логирования.

Конфигурация логгеров для всех компонентов приложения.
"""

import json
import logging
import sys
from typing import Optional


def disable_aiogram_logs() -> None:
    """Отключает избыточные логи aiogram."""
    for name in ["aiogram.middlewares", "aiogram.event", "aiohttp.access"]:
        logging.getLogger(name).setLevel(logging.WARNING)


class JSONFormatter(logging.Formatter):
    """Форматтер для JSON логов."""
    
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Добавляем exception info если есть
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Добавляем extra поля
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 
                          'exc_text', 'stack_info']:
                log_entry[key] = value
        
        return json.dumps(log_entry, ensure_ascii=False)


def setup_logger(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    log_format: str = "%(asctime)s %(levelname)s | %(name)s: %(message)s",
    date_format: str = "[%Y-%m-%d %H:%M:%S]",
    json_format: bool = False
) -> None:
    """
    Настраивает основную систему логирования.
    
    Args:
        level: Уровень логирования
        log_file: Путь к файлу логов (опционально)
        log_format: Формат сообщений логов
        date_format: Формат даты/времени
        json_format: Использовать JSON формат для Elasticsearch
    """
    # Выбор форматтера
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(log_format, date_format)
    
    # Настройка обработчика для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    # Настройка корневого логгера
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # Добавление файлового обработчика, если указан файл
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        root_logger.addHandler(file_handler)
    
    # Отключение избыточных логов
    disable_aiogram_logs()


def get_logger(name: str) -> logging.Logger:
    """
    Получает логгер с указанным именем.
    
    Args:
        name: Имя логгера
        
    Returns:
        Настроенный логгер
    """
    return logging.getLogger(name)
