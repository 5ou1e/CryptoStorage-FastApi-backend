from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.infra.db.setup_tortoise import (
    register_db,
)
from src.presentation.api.exceptions import (
    setup_exception_handlers,
)
from src.presentation.api.middlewares import (
    setup_middlewares,
)
from src.presentation.api.routers import (
    setup_routers,
)
from src.settings import config
from src.settings.logging import setup_logging


class AppBuilder:
    """Создает и настраивает приложение."""

    @staticmethod
    def create_app() -> FastAPI:
        app = FastAPI(
            default_response_class=ORJSONResponse,
            title="CryptoStorage API",
            openapi_url=f"{config.api.prefix}/openapi.json",
            docs_url=f"{config.api.prefix}/docs",
            redoc_url=f"{config.api.prefix}/redoc",
            swagger_ui_parameters={
                "persistAuthorization": True
            },  # Сохраняет авторизацию при перезагрузке страницы доки
        )
        # register_db(app)
        setup_routers(app)
        setup_middlewares(app)
        setup_exception_handlers(app)
        setup_logging()
        return app
