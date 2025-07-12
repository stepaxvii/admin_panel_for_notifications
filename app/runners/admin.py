"""
Админ-панель для управления Telegram ботом.

Предоставляет веб-интерфейс для создания и отправки уведомлений пользователям бота.
"""

from app.admin.app import run_admin_app

if __name__ == "__main__":
    run_admin_app() 