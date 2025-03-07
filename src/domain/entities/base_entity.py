from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class BaseEntity(ABC):
    """Абстрактный класс Entity"""

    pass


@dataclass(kw_only=True)
class TimestampMixinEntity:
    """Миксин с timestamp-полями"""

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
