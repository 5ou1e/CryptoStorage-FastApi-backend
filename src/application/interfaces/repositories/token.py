from abc import ABC
from typing import TypeVar

from src.application.interfaces.repositories.generic_repository import (
    BaseGenericRepository,
)
from src.domain.entities.base_entity import BaseEntity
from src.domain.entities.token import TokenEntity, TokenPriceEntity


class BaseTokenRepository(BaseGenericRepository[TokenEntity], ABC):
    """Интерфейс репозитория Token"""

    async def get_by_address(self, address: str) -> TokenEntity | None:
        raise NotImplementedError


class BaseTokenPriceRepository(BaseGenericRepository[TokenPriceEntity], ABC):
    """Интерфейс репозитория Token-price"""

    pass
