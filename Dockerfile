FROM python:3.12-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка uv
RUN pip install --upgrade pip && \
    pip install uv

# Создание пользователя
RUN useradd --create-home --shell /bin/bash app

# Установка рабочей директории
WORKDIR /app

# Копирование файлов проекта
COPY pyproject.toml .
COPY requirements-dev.txt .

# Установка зависимостей проекта через uv (с флагом --system)
RUN uv pip install --system .

# Копирование остальных файлов
COPY . .

# Смена владельца файлов
RUN chown -R app:app /app

# Создание файла для логирования
RUN touch /app/logs.log

# Переключение на пользователя app
USER app

# Открытие порта
EXPOSE 8080

# Команда по умолчанию
CMD ["python", "-m", "app"]
