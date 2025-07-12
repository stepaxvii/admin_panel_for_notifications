"""
Автоматическая загрузка переменных окружения и настройка POSTGRES_HOST.

Автоматически определяет окружение и устанавливает правильный хост для PostgreSQL.
"""

import os
from pathlib import Path


def auto_env_patch() -> None:
    """
    Загружает .env файл и автоматически устанавливает POSTGRES_HOST:
    
    - ENVIRONMENT=docker  => POSTGRES_HOST=postgres
    - ENVIRONMENT=local   => POSTGRES_HOST=localhost
    - ENVIRONMENT=auto (по умолчанию):
        - если /.dockerenv существует => POSTGRES_HOST=postgres
        - иначе => POSTGRES_HOST=localhost
    """
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key, value)
    
    env = os.getenv("ENVIRONMENT", "auto")
    if env == "docker":
        db_host = "postgres"
    elif env == "local":
        db_host = "localhost"
    else:
        if os.path.exists("/.dockerenv"):
            db_host = "postgres"
        else:
            db_host = "localhost"
    os.environ["POSTGRES_HOST"] = db_host

    # Автоматическая сборка DATABASE_URL
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_pass = os.getenv("POSTGRES_PASSWORD", "postgres")
    db_name = os.getenv("POSTGRES_DB", "postgres")
    db_port = os.getenv("POSTGRES_PORT", "5432")
    db_host = os.getenv("POSTGRES_HOST", db_host)
    os.environ["DATABASE_URL"] = f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}" 