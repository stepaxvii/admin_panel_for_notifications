import logging

import app.celery.celery_tasks.notification
from app.celery.celery_app import celery_app
from app.utils.logging import setup_logger

setup_logger(level=logging.INFO, log_file="logs.log")
