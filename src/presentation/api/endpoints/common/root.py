from fastapi import APIRouter
from starlette.responses import RedirectResponse

from src.settings import config

router = APIRouter()


# Редирект с главной страницы на /docs
@router.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url=f"{config.api.prefix}/docs")
