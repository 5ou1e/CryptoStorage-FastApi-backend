import asyncio
import datetime
from collections import defaultdict
from itertools import chain
from typing import Iterable, List, Optional

import numpy as np
from tortoise import Model

from src.infra.db.models.tortoise import (
    FlipsideCryptoAccount,
    FlipsideCryptoConfig,
    Swap,
    Token,
    TokenPrice,
    Wallet,
    WalletDetail,
    WalletStatistic7d,
    WalletStatistic30d,
    WalletStatisticAll,
    WalletToken,
)
from src.infra.db.repositories import (
    SwapRepository,
    TokenRepository,
    WalletDetailRepository,
    WalletRepository,
    WalletStatistic7dRepository,
    WalletStatistic30dRepository,
    WalletStatisticAllRepository,
    WalletTokenRepository,
)

from .config import *


async def get_flipside_account():
    return await FlipsideCryptoAccount.filter(is_active=True).first()


async def get_flipside_config():
    return await FlipsideCryptoConfig.first()


async def set_flipside_account_inactive(
    flipside_account,
):
    flipside_account.is_active = False
    await flipside_account.save()


async def update_flipside_config_swaps_parsed_untill(flipside_config, parsed_untill):
    flipside_config.swaps_parsed_untill_inserted_timestamp = parsed_untill
    await flipside_config.save()


async def get_sol_prices(
    minute_from: datetime,
    minute_to: datetime,
):
    sol_token = await Token.filter(address=SOL_ADDRESS).first()
    if not sol_token:
        raise ValueError(f"Токен WSOL не найден в БД!")
    _sol_prices = await TokenPrice.filter(
        token=sol_token,
        minute__gte=minute_from,
        minute__lte=minute_to,
    ).all()
    sol_prices = {price.minute: price.price_usd for price in _sol_prices}
    return sol_prices


async def bulk_create_parallel(
    repository_class,
    records: List[Model],
    chunks_count: int = 5,
    ignore_conflicts: bool = True,
    on_conflict: Optional[list] = None,
    update_fields: Optional[Iterable[str]] = None,  # Поля для обновления
):
    repository = repository_class()
    chunks = np.array_split(records, chunks_count)
    await asyncio.gather(
        *[
            repository.bulk_create(
                chunks[i].tolist(),
                ignore_conflicts=ignore_conflicts,
                on_conflict=on_conflict,
                update_fields=update_fields,  # Поля для обновления
            )
            for i in range(chunks_count)
        ]
    )


async def import_wallets(wallets, chunks_count=10) -> dict:
    await bulk_create_parallel(
        WalletRepository,
        wallets,
        chunks_count=chunks_count,
    )
    wallet_repository = WalletRepository()
    created_addresses = list({wallet.address for wallet in wallets})
    # Разбиваем список адресов на части, если их больше, чем PostgreSQL позволяет в одном запросе
    batch_size = 30000
    id_batches = [created_addresses[i : i + batch_size] for i in range(0, len(created_addresses), batch_size)]
    wallets_map = {}
    for batch in id_batches:
        res = await Wallet.in_bulk(batch, "address")
        created_wallets = [wallet for wallet in res.values()]
        await Wallet.fetch_for_list(
            created_wallets,
            "details",
            "stats_7d",
            "stats_30d",
            "stats_all",
        )
        wallets_map.update(res)

    return wallets_map


async def import_tokens(tokens, chunks_count=10) -> dict:
    await bulk_create_parallel(TokenRepository, tokens, chunks_count)
    created_addresses = list({token.address for token in tokens})
    # Разбиваем список адресов на части, если их больше, чем PostgreSQL позволяет в одном запросе
    batch_size = 30000  # или другое значение, подходящее для вашей базы
    id_batches = [created_addresses[i : i + batch_size] for i in range(0, len(created_addresses), batch_size)]
    tokens_map = {}
    for batch in id_batches:
        res = await Token.in_bulk(batch, "address")
        tokens_map.update(res)
    return tokens_map


async def create_wallet_details(records: List[Model], chunks_count: int = 10) -> None:
    await bulk_create_parallel(
        WalletDetailRepository,
        records,
        chunks_count,
    )


async def update_wallets(records: List[Model], chunks_count: int = 10) -> None:
    chunks = np.array_split(records, chunks_count)
    await asyncio.gather(
        *[
            WalletRepository().bulk_update_last_activity_timestamp(objects=chunks[i].tolist())
            for i in range(chunks_count)
        ]
    )


async def create_wallet_statistics_7d(records: List[Model], chunks_count: int = 5) -> None:
    await bulk_create_parallel(
        WalletStatistic7dRepository,
        records,
        chunks_count,
    )


async def create_wallet_statistics_30d(records: List[Model], chunks_count: int = 5) -> None:
    await bulk_create_parallel(
        WalletStatistic30dRepository,
        records,
        chunks_count,
    )


async def create_wallet_statistics_all(records: List[Model], chunks_count: int = 5) -> None:
    await bulk_create_parallel(
        WalletStatisticAllRepository,
        records,
        chunks_count,
    )


async def import_activities(activities: List[Model], chunks_count: int = 5) -> None:
    await bulk_create_parallel(SwapRepository, activities, chunks_count)


async def load_wallet_tokens(token_wallet_list, chunks_count: int = 5) -> list[Model]:
    # Загружаем записи WalletToken параллельно
    async def _load(token_wallet_list_):
        token_wallet_ids = defaultdict(list)
        for item in token_wallet_list_:
            token_wallet_ids[item["token_id"]].append(item["wallet_id"])
        all_wt_stats = []
        for (
            token_id,
            wallet_ids,
        ) in token_wallet_ids.items():
            existing_wallet_token_stats = await WalletToken.filter(
                token_id=token_id,
                wallet_id__in=wallet_ids,
            ).all()
            if existing_wallet_token_stats:
                all_wt_stats.extend(existing_wallet_token_stats)
        return all_wt_stats

    token_wallet_list_chunks = np.array_split(token_wallet_list, chunks_count)
    results = await asyncio.gather(*[_load(token_wallet_list_chunks[i]) for i in range(chunks_count)])
    return list(chain(*results))


async def import_wallet_tokens(
    wallet_token_records: List[Model],
    chunks_count=5,
):
    fields_to_update = WalletToken._meta.db_fields.copy()  # Обязательно .copy(), чтобы не менять исходный set
    fields_to_update.remove("id")
    fields_to_update.remove("created_at")
    await bulk_create_parallel(
        WalletTokenRepository,
        wallet_token_records,
        chunks_count,
        ignore_conflicts=False,
        on_conflict=["wallet_id", "token_id"],
        update_fields=fields_to_update,  # Поля для обновления
    )
