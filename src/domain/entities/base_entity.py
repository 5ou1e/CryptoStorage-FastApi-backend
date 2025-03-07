from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from mashumaro.types import SerializationStrategy


class TsSerializationStrategy(SerializationStrategy, use_annotations=False):
    def serialize(self, value: datetime) -> datetime:
        return value

    # def deserialize(self, value: float) -> datetime:
    #     # value will be converted to float before being passed to this method
    #     return datetime.fromtimestamp(value)


@dataclass
class BaseEntity(ABC):
    """Абстрактный класс Entity"""

    class Config:
        serialization_strategy = {
            datetime: TsSerializationStrategy(),
        }



@dataclass(kw_only=True)
class TimestampMixinEntity:
    """Миксин с timestamp-полями"""

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
