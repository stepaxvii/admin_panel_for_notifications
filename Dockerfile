FROM python:3.12-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Обновление pip и setuptools для поддержки pyproject.toml
RUN pip install --upgrade pip setuptools

# Создание пользователя
RUN useradd --create-home --shell /bin/bash app

# Установка рабочей директории
WORKDIR /app

# Копирование файлов проекта
ADD . /app

# Копирование скрипта запуска админки
COPY scripts/start-admin.sh /app/scripts/start-admin.sh
RUN chmod +x /app/scripts/start-admin.sh

# Установка зависимостей проекта из requirements.txt
RUN pip install -r requirements.txt

# Диагностика: вывод установленных пакетов
RUN pip list

# Смена владельца файлов
RUN chown -R app:app /app

# Переключение на пользователя app
USER app

# Открытие порта
EXPOSE 8080

# Команда по умолчанию
CMD ["python", "-m", "app"]
