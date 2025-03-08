import asyncio
import datetime
from collections import defaultdict
from itertools import chain
from typing import List

import numpy as np
from tortoise import Model
from tortoise.transactions import in_transaction

from src.infra.db.models.tortoise import (
    FlipsideCryptoAccount,
    FlipsideCryptoConfig,
    Token,
    TokenPrice,
    Wallet,
    WalletToken,
)
from src.infra.db.repositories.tortoise import (
    TortoiseSwapRepository,
    TortoiseTokenRepository,
    TortoiseWalletDetailRepository,
    TortoiseWalletRepository,
    TortoiseWalletStatistic7dRepository,
    TortoiseWalletStatistic30dRepository,
    TortoiseWalletStatisticAllRepository,
    TortoiseWalletTokenRepository,
)

from . import utils
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


async def import_wallets_data(wallets, chunks_count=10) -> list[Wallet]:
    """Создаем кошельки и все их связи в несколько тасков"""
    chunks = np.array_split(wallets, chunks_count)
    results = await asyncio.gather(*[import_wallets_data_chunk(chunks[i].tolist()) for i in range(chunks_count)])
    created_wallets = [wallet for result in results for wallet in result]
    return created_wallets


async def import_wallets_data_chunk(
    wallets,
) -> list[Wallet]:
    """Импортируем кошельки со всеми связями в одной транзакции"""
    repository = TortoiseWalletRepository()
    async with in_transaction() as conn:
        await repository.bulk_create(objects=wallets, ignore_conflicts=True)
        created_addresses = list({wallet.address for wallet in wallets})
        created_wallets: list[Wallet] = await repository.get_list(filter_by={"address__in": created_addresses})
        (
            wallet_details,
            wallet_stats_7d,
            wallet_stats_30d,
            wallet_stats_all,
        ) = utils.create_wallets_relations(created_wallets)
        await asyncio.gather(
            TortoiseWalletStatistic7dRepository().bulk_create(wallet_stats_7d),
            TortoiseWalletStatistic30dRepository().bulk_create(wallet_stats_30d),
            TortoiseWalletStatisticAllRepository().bulk_create(wallet_stats_all),
            TortoiseWalletDetailRepository().bulk_create(wallet_details),
        )
        return created_wallets


async def import_tokens(tokens, chunks_count=5) -> list[Token]:
    chunks = np.array_split(tokens, chunks_count)
    results = await asyncio.gather(*[import_tokens_chunk(chunks[i].tolist()) for i in range(chunks_count)])
    return [token for result in results for token in result]


async def import_tokens_chunk(
    tokens,
) -> list[Token]:
    repository = TortoiseTokenRepository()
    await repository.bulk_create(tokens)
    return await repository.get_list(filter_by={"address__in": [token.address for token in tokens]})


async def update_wallets(records: List[Model], chunks_count: int = 10) -> None:
    chunks = np.array_split(records, chunks_count)
    await asyncio.gather(
        *[
            TortoiseWalletRepository().bulk_update(
                objects=chunks[i].tolist(),
                fields=[
                    "first_activity_timestamp",
                    "last_activity_timestamp",
                ],
            )
            for i in range(chunks_count)
        ]
    )


async def import_activities(
    activities: List[Model],
) -> None:
    await TortoiseSwapRepository().bulk_create(activities)


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
    records: List[Model],
):
    fields_to_update = WalletToken._meta.db_fields.copy()
    fields_to_update.remove("id")
    fields_to_update.remove("wallet_id")
    fields_to_update.remove("token_id")
    fields_to_update.remove("created_at")
    await TortoiseWalletTokenRepository().bulk_create(
        records,
        ignore_conflicts=False,
        on_conflict=["wallet_id", "token_id"],
        update_fields=fields_to_update,
    )
