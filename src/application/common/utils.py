import math
from typing import List, Type, TypeVar

from pydantic import BaseModel

from src.application.common.dto import Pagination, PaginationResult

T = TypeVar("T", bound=PaginationResult)


def create_paginated_response(
    data: List[BaseModel],  # Данные для ответа
    total_count: int,  # Общее количество элементов
    pagination: Pagination,  # Данные запросы страницы
    response_model: Type[PaginationResult],  # Модель для ответа
    data_field: str,  # Название поля для данных (например, "wallets", "tokens")
) -> T:
    """
    Функция создает ответ с пагинацией, заполняя переданные данные в соответствующую модель.
    """
    per_page = pagination.per_page
    total_pages = math.ceil(total_count / per_page)
    count = len(data)
    response_data = {data_field: data}  # Данные, которые должны быть вложены в модель
    return response_model(
        page=pagination.page,
        per_page=pagination.per_page,
        count=count,
        total_count=total_count,
        total_pages=total_pages,
        **response_data
    )


def classify_block_relation(event_block: int, reference_block: int) -> str:
    if event_block < reference_block:
        return "before"
    elif event_block > reference_block:
        return "after"
    return "same"


def classify_token_trade_status(buy_status: str, sell_status: str):
    if (buy_status, sell_status) in [
        ("after", "after"),
        ("same", "after"),
        ("after", "same"),
    ]:
        status = "after"
    elif (buy_status, sell_status) in [
        ("same", "before"),
        ("before", "before"),
        ("before", "same"),
    ]:
        status = "before"
    elif (buy_status, sell_status) == ("same", "same"):
        status = "same"
    else:
        # ("before", "after"),
        # ("after", "before"),
        status = "mixed"
    return status


def classify_related_wallet_status(statuses_: set):
    if statuses_ == {"same"}:
        status = "similar"
    elif statuses_ <= {"after", "same"}:
        status = "copied_by"
    elif statuses_ <= {"before", "same"}:
        status = "copying"
    else:
        status = "similar"  # если есть mixed
    return status
