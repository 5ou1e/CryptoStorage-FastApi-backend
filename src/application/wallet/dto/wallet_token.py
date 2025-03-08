from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from fastapi import Query
from pydantic import BaseModel

from src.application.common.dto import (
    PaginationResult,
)
from src.application.token.dto import TokenDTO


class GetWalletTokensFilters(BaseModel):
    created_at__gte: Optional[datetime] = Query(None)
    created_at__lte: Optional[datetime] = Query(None)
    total_profit_usd__gte: Optional[float] = Query(None)
    total_profit_usd__lte: Optional[float] = Query(None)


class WalletTokenDTO(BaseModel):
    token: TokenDTO
    total_buys_count: Optional[int] = None
    total_buy_amount_usd: Optional[Decimal] = None
    total_buy_amount_token: Optional[Decimal] = None
    first_buy_price_usd: Optional[Decimal] = None
    first_buy_timestamp: Optional[int] = None
    total_sales_count: Optional[int] = None
    total_sell_amount_usd: Optional[Decimal] = None
    total_sell_amount_token: Optional[Decimal] = None
    first_sell_price_usd: Optional[Decimal] = None
    first_sell_timestamp: Optional[int] = None
    last_activity_timestamp: Optional[int] = None
    total_profit_usd: Optional[Decimal] = None
    total_profit_percent: Optional[float] = None
    first_buy_sell_duration: Optional[int] = None
    total_swaps_from_txs_with_mt_3_swappers: Optional[int] = None
    total_swaps_from_arbitrage_swap_events: Optional[int] = None

    class Config:
        from_attributes = True


class WalletTokensDTO(BaseModel):
    wallet_tokens: List[WalletTokenDTO]


class WalletTokensPageDTO(WalletTokensDTO, PaginationResult):
    pass
