import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    DECIMAL,
    UUID,
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infra.db.models.sqlalchemy.base import (
    Base,
    IntIDMixin,
    TimestampsMixin,
    UUIDIDMixin,
)


class Wallet(Base, UUIDIDMixin, TimestampsMixin):
    __tablename__ = "wallet"

    address: Mapped[str] = mapped_column(String(90), unique=True, nullable=False)
    last_stats_check: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_activity_timestamp: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    first_activity_timestamp: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    # Связи
    details = relationship("WalletDetail", back_populates="wallet", uselist=False)
    stats_7d = relationship("WalletStatistic7d", back_populates="wallet", uselist=False)
    stats_30d = relationship(
        "WalletStatistic30d", back_populates="wallet", uselist=False
    )
    stats_all = relationship(
        "WalletStatisticAll", back_populates="wallet", uselist=False
    )

    __table_args__ = (
        Index("idx_wallet_created_at", "created_at"),
        Index("idx_wallet_last_activity", "last_activity_timestamp"),
        Index("idx_wallet_address", "address"),
    )

    def __str__(self):
        return f"{self.address}"


class WalletDetail(Base, IntIDMixin, TimestampsMixin):
    __tablename__ = "wallet_detail"

    wallet_id: Mapped["Wallet.id.type"] = mapped_column(
        ForeignKey("wallet.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    sol_balance: Mapped[Decimal] = mapped_column(DECIMAL(50, 20), nullable=True)
    is_scammer: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_bot: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    wallet: Mapped["Wallet"] = relationship(
        "Wallet", back_populates="details", uselist=False
    )

    __table_args__ = (
        Index("idx_wallet_detail_is_bot", "is_bot"),
        Index("idx_wallet_detail_is_scammer", "is_scammer"),
    )

    def __str__(self):
        return f"WalletDetail(id={self.id}, wallet_id={self.wallet_id})"


class AbstractWalletStatistic(Base, IntIDMixin, TimestampsMixin):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    wallet_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("wallet.id"), unique=True, nullable=False
    )

    winrate: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(40, 5), index=True)
    total_token_buy_amount_usd: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(50, 20)
    )
    total_token_sell_amount_usd: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(50, 20)
    )
    total_profit_usd: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(50, 20), index=True
    )
    total_profit_multiplier: Mapped[Optional[float]] = mapped_column(Float, index=True)
    total_token: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    total_token_buys: Mapped[Optional[int]] = mapped_column(Integer)
    total_token_sales: Mapped[Optional[int]] = mapped_column(Integer)
    token_with_buy_and_sell: Mapped[Optional[int]] = mapped_column(Integer)
    token_with_buy: Mapped[Optional[int]] = mapped_column(Integer)
    token_sell_without_buy: Mapped[Optional[int]] = mapped_column(Integer)
    token_buy_without_sell: Mapped[Optional[int]] = mapped_column(Integer)
    token_with_sell_amount_gt_buy_amount: Mapped[Optional[int]] = mapped_column(Integer)
    token_avg_buy_amount: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(50, 20), index=True
    )
    token_median_buy_amount: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(50, 20))
    token_first_buy_avg_price_usd: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(50, 20)
    )
    token_first_buy_median_price_usd: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(50, 20), index=True
    )
    token_avg_profit_usd: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(50, 20), index=True
    )
    token_buy_sell_duration_avg: Mapped[Optional[int]] = mapped_column(BigInteger)
    token_buy_sell_duration_median: Mapped[Optional[int]] = mapped_column(
        BigInteger, index=True
    )
    first_transaction_timestamp: Mapped[Optional[int]] = mapped_column(BigInteger)
    pnl_lt_minus_dot5_num: Mapped[Optional[int]] = mapped_column(Integer)
    pnl_minus_dot5_0x_num: Mapped[Optional[int]] = mapped_column(Integer)
    pnl_lt_2x_num: Mapped[Optional[int]] = mapped_column(Integer)
    pnl_2x_5x_num: Mapped[Optional[int]] = mapped_column(Integer)
    pnl_gt_5x_num: Mapped[Optional[int]] = mapped_column(Integer)
    pnl_lt_minus_dot5_percent: Mapped[Optional[float]] = mapped_column(Float)
    pnl_minus_dot5_0x_percent: Mapped[Optional[float]] = mapped_column(Float)
    pnl_lt_2x_percent: Mapped[Optional[float]] = mapped_column(Float)
    pnl_2x_5x_percent: Mapped[Optional[float]] = mapped_column(Float)
    pnl_gt_5x_percent: Mapped[Optional[float]] = mapped_column(Float)

    total_swaps_from_arbitrage_swap_events: Optional[int] = 0
    total_swaps_from_txs_with_mt_3_swappers: Optional[int] = 0

    @property
    def total_buys_and_sales_count(self) -> int:
        return (self.total_token_buys or 0) + (self.total_token_sales or 0)


class WalletStatistic7d(AbstractWalletStatistic):
    __tablename__ = "wallet_statistic_7d"

    wallet = relationship("Wallet", back_populates="stats_7d", uselist=False)

    def __str__(self):
        return "Статистика кошелька за 7д"


class WalletStatistic30d(AbstractWalletStatistic):
    __tablename__ = "wallet_statistic_30d"

    wallet = relationship("Wallet", back_populates="stats_30d", uselist=False)

    def __str__(self):
        return "Статистика кошелька за 30д"


class WalletStatisticAll(AbstractWalletStatistic):
    __tablename__ = "wallet_statistic_all"

    wallet = relationship("Wallet", back_populates="stats_all", uselist=False)

    def __str__(self):
        return "Статистика кошелька за все время"


class WalletStatisticBuyPriceGt15k7d(AbstractWalletStatistic):
    __tablename__ = "wallet_statistic_buy_price_gt_15k_7d"

    wallet = relationship("Wallet", backref="stats_buy_price_gt_15k_7d", uselist=False)

    def __str__(self):
        return "Статистика кошелька за 7д"


class WalletStatisticBuyPriceGt15k30d(AbstractWalletStatistic):
    __tablename__ = "wallet_statistic_buy_price_gt_15k_30d"

    wallet = relationship("Wallet", backref="stats_buy_price_gt_15k_30d", uselist=False)

    def __str__(self):
        return "Статистика кошелька за 30д"


class WalletStatisticBuyPriceGt15kAll(AbstractWalletStatistic):
    __tablename__ = "wallet_statistic_buy_price_gt_15k_all"

    wallet = relationship("Wallet", backref="stats_buy_price_gt_15k_all", uselist=False)

    def __str__(self):
        return "Статистика кошелька за все время"


class WalletToken(Base, UUIDIDMixin, TimestampsMixin):
    __tablename__ = "wallet_token"

    total_buys_count: Mapped[int] = mapped_column(Integer, default=0)
    total_buy_amount_usd: Mapped[Decimal] = mapped_column(DECIMAL(40, 20), default=0)
    total_buy_amount_token: Mapped[Decimal] = mapped_column(DECIMAL(40, 20), default=0)
    first_buy_price_usd: Mapped[Decimal] = mapped_column(DECIMAL(40, 20), nullable=True)
    first_buy_timestamp: Mapped[int] = mapped_column(BigInteger, nullable=True)

    total_sales_count: Mapped[int] = mapped_column(Integer, default=0)
    total_sell_amount_usd: Mapped[Decimal] = mapped_column(DECIMAL(40, 20), default=0)
    total_sell_amount_token: Mapped[Decimal] = mapped_column(DECIMAL(40, 20), default=0)
    first_sell_price_usd: Mapped[Decimal] = mapped_column(
        DECIMAL(40, 20), nullable=True
    )
    first_sell_timestamp: Mapped[int] = mapped_column(BigInteger, nullable=True)

    last_activity_timestamp: Mapped[int] = mapped_column(BigInteger, nullable=True)
    total_profit_usd: Mapped[Decimal] = mapped_column(DECIMAL(40, 20), default=0)
    total_profit_percent: Mapped[float] = mapped_column(Float, nullable=True)
    first_buy_sell_duration: Mapped[int] = mapped_column(Integer, nullable=True)

    total_swaps_from_txs_with_mt_3_swappers: Mapped[int] = mapped_column(
        Integer, default=0
    )
    total_swaps_from_arbitrage_swap_events: Mapped[int] = mapped_column(
        Integer, default=0
    )

    wallet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wallet.id", ondelete="CASCADE"), index=True
    )
    token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("token.id", ondelete="CASCADE"), index=True
    )

    wallet = relationship("Wallet", backref="tokens")
    token = relationship("Token", backref="wallets")

    __table_args__ = (
        UniqueConstraint("wallet_id", "token_id", name="uq_wallet_token"),
        Index("idx_wallet", "wallet_id"),
        Index("idx_token", "token_id"),
    )


class TgSentWallet(Base, IntIDMixin, TimestampsMixin):
    __tablename__ = "tg_sent_wallet"

    wallet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wallet.id", ondelete="CASCADE"), unique=True
    )

    wallet = relationship("Wallet", backref="tg_sent")
