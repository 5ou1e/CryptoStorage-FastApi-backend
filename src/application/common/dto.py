from fastapi import Query
from pydantic import BaseModel


class Pagination(BaseModel):
    page: int = Query(1, ge=1, description="Номер страницы")
    page_size: int = Query(
        10,
        ge=1,
        le=100,
        description="Кол-во элементов на странице",
    )


class PaginationResult(BaseModel):
    page: int
    page_size: int
    count: int
    total_count: int
    total_pages: int
