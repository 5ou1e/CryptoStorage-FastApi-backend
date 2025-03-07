from abc import ABC, abstractmethod
from typing import Any, Generic, TypeAlias, TypeVar
from uuid import UUID

from src.domain.entities.base_entity import BaseEntity

Entity = TypeVar("Entity", bound=BaseEntity)


class BaseGenericRepository(Generic[Entity], ABC):
    """Интерфейс универсального репозитория"""

    @abstractmethod
    async def get_by_id(self, id_: Any) -> Entity | None:
        raise NotImplementedError

    @abstractmethod
    async def get_list(
        self,
        limit: int = None,
        offset: int = None,
    ) -> list[Entity]:
        raise NotImplementedError

    @abstractmethod
    async def get_page(
        self,
        page: int = 1,
        per_page: int = 10,
    ) -> list[Entity]:
        raise NotImplementedError

    @abstractmethod
    async def get_count(self) -> int:
        raise NotImplementedError

    @abstractmethod
    async def create(self, entity: Entity) -> Entity:
        raise NotImplementedError

    @abstractmethod
    async def update(self, entity: Entity):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, entity: Entity):
        raise NotImplementedError

    @abstractmethod
    async def bulk_create(self, entities: list[Entity]) -> list[Entity]:
        raise NotImplementedError

    @abstractmethod
    async def bulk_update(self, entities: list[Entity]) -> list[Entity]:
        raise NotImplementedError

    # def __getitem__(self, index) -> Entity:
    #     return self.get_by_id(index)
