import os

from aiogram import Bot, Dispatcher
from fastapi import FastAPI
import starlette_admin
from starlette.staticfiles import StaticFiles

from app.admin.admin_app import setup_admin
from app.endpoints import healthcheck
from app.endpoints.notification import router as notification_router

admin = setup_admin()


def setup_fastapi(app: FastAPI, dispatcher: Dispatcher, bot: Bot) -> FastAPI:
    app.include_router(healthcheck.router)
    app.include_router(notification_router)
    admin.mount_to(app)
    static_path = os.path.join(os.path.dirname(starlette_admin.__file__), "statics")
    app.mount("/statics", StaticFiles(directory=static_path), name="statics")
    for key, value in dispatcher.workflow_data.items():
        setattr(app.state, key, value)
    app.state.dispatcher = dispatcher
    app.state.bot = bot
    app.state.shutdown_completed = False
    return app
