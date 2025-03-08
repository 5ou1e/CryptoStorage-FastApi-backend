import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DECIMAL,
    UUID,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from .base import (
    Base,
    IntIDMixin,
    TimestampsMixin,
    UUIDIDMixin,
)


class Token(Base, UUIDIDMixin, TimestampsMixin):
    __tablename__ = "token"

    address: Mapped[str] = mapped_column(String(90), unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    symbol: Mapped[str | None] = mapped_column(String(100), nullable=True)
    uri: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Token Metaplex Metadata Uri",
    )
    logo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_on: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Создан на",
    )
    is_metadata_parsed: Mapped[bool] = mapped_column(Boolean, default=False)

    def __str__(self):
        return self.address


class TokenPrice(Base, IntIDMixin, TimestampsMixin):
    __tablename__ = "token_price"

    token_id: Mapped["Token.id.type"] = mapped_column(ForeignKey("token.id"), nullable=False)
    token: Mapped["Token"] = relationship("Token", backref="token_price")
    price_usd: Mapped[Decimal | None] = mapped_column(DECIMAL(40, 20), nullable=True)
    minute: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "token_id",
            "minute",
            name="_token_minute_uc",
        ),
    )

    def __str__(self):
        return f"Цена {self.token.symbol} в {self.minute}"
