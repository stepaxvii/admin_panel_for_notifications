from celery import Celery

from app.models.config.env import RedisConfig

redis_config = RedisConfig()  # type: ignore
redis_url = redis_config.build_url()

celery_app = Celery(
    "mass_send",
    broker=redis_url,
    backend=redis_url,
)

celery_app.conf.task_routes = {
    "app.celery.celery_tasks.notification.*": {"queue": "notifications"}
}
