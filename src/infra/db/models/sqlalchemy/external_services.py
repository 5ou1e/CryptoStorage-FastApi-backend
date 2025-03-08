from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infra.db.models.sqlalchemy.base import (
    Base,
    IntIDMixin,
)


class FlipsideCryptoConfig(Base, IntIDMixin):
    __tablename__ = "flipsidecrypto_config"

    # TODO: swaps_parsed_untill_inserted_timestamp - сейчас это BLOCK_TIMESTAMP
    swaps_parsed_untill_inserted_timestamp: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    __table_args__ = {"comment": "Конфиг FlipsideCrypto"}


class FlipsideCryptoAccount(Base, IntIDMixin):
    __tablename__ = "flipsidecrypto_account"

    api_key: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = {"comment": "Аккаунты FlipsideCrypto"}
