from sqlalchemy.ext.asyncio import create_async_engine
from starlette_admin.contrib.sqla import Admin, ModelView

from app.admin.views.notification_view import NotificationView
from app.factory.app_config import create_app_config
from app.models.sql.notification import Notification
from app.models.sql.user import User


def setup_admin():
    config = create_app_config()
    engine = create_async_engine(config.postgres.build_url())
    admin = Admin(engine, title="Admin Panel")
    admin.add_view(NotificationView(Notification))
    admin.add_view(ModelView(User))
    return admin
