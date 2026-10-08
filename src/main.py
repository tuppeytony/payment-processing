from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI

from api.v1 import payments
from broker import broker
from common import configure_logging
from config import app_settings
from exception_handlers import create_exception_handlers
from middlewares import AuthMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, None]:  # noqa: ARG001
    """Жизненный цикл приложения."""
    await broker.start()
    yield
    await broker.stop()


app = FastAPI(
    debug=app_settings.debug,
    title=app_settings.title,
    lifespan=lifespan,
)
if not app_settings.debug:
    app.add_middleware(AuthMiddleware, x_api_key=app_settings.x_api_key)

app.include_router(payments.router, prefix="/api/v1")

create_exception_handlers(app)

if __name__ == "__main__":
    configure_logging(app_settings.log_level)
    uvicorn.run(
        app,
        log_level=app_settings.log_level,
        host=app_settings.host,
        port=app_settings.port,
    )
