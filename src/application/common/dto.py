from fastapi import Query
from pydantic import BaseModel


class Pagination(BaseModel):
    page: int = Query(1, ge=1, description="Номер страницы")
    per_page: int = Query(
        10, ge=1, le=100, description="Количество элементов на странице"
    )


class PaginationResult(BaseModel):
    page: int
    per_page: int
    count: int
    total_count: int
    total_pages: int
