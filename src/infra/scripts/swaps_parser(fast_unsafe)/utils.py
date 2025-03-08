import uuid
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Tuple

import pytz

from src.infra.db.models.tortoise import (
    Swap,
    Token,
    Wallet,
    WalletDetail,
    WalletStatistic7d,
    WalletStatistic30d,
    WalletStatisticAll,
    WalletToken,
)

from .config import SOL_ADDRESS
from .logger import logger


def create_wallet_token_ids_list(
    activities: list[Swap],
):
    result = []
    unique_pairs = set()
    for activity in activities:
        pair = (
            activity.wallet_id,
            activity.token_id,
        )
        if pair not in unique_pairs:
            unique_pairs.add(pair)
            result.append(
                {
                    "wallet_id": activity.wallet_id,
                    "token_id": activity.token_id,
                }
            )
    return result


def populate_swaps_data(mapped_swaps: dict):
    """Дополняет данные свапов дополнительной информацией"""
    okx_wallet = "HV1KXxWFaSeriyFvXyx48FqG9BoFbfinB8njCJonqP7K"
    for tx_id, _swaps in mapped_swaps.items():
        swappers = defaultdict(lambda: defaultdict(list))
        swaps_count = len(_swaps)
        for swap in _swaps:
            token = (
                swap["swap_from_mint"]
                if swap["swap_to_mint"] == "So11111111111111111111111111111111111111112"
                else swap["swap_to_mint"]
            )
            event_type = "buy" if swap["swap_to_mint"] == token else "sell"
            swappers[swap["swapper"]][token].append(event_type)
        swappers_list = [swapper for swapper in swappers.keys()]
        swappers_count = len(swappers_list)
        if swaps_count >= 2:
            if swappers_count == 1:
                for swap in _swaps:
                    for token, events in swappers[swap["swapper"]].items():
                        if len(events) >= 2 and ("buy" in events and "sell" in events):
                            swap["is_part_of_arbitrage_swap_event"] = True
            elif swappers_count == 2:
                if okx_wallet in swappers_list:
                    real_swapper = swappers_list[0] if swappers_list[1] == okx_wallet else swappers_list[1]
                    for swap in _swaps:
                        swap["swapper"] = real_swapper
            elif swappers_count >= 3:
                for swap in _swaps:
                    swap["is_part_of_transaction_with_mt_3_swappers"] = True


def combine_swaps(swaps: list[dict], swaps_jupiter: list[dict]):
    """Обьединяет свапы с двух источников"""
    mapped_swaps_jupiter = defaultdict(list)
    for swap in swaps_jupiter:
        if (
            not swap["swapper"] == None
        ):  # Бывает что swapper - None , тогда не записываем свап как Jupiter-Swap, чтобы учитывался свап из другой таблицы
            mapped_swaps_jupiter[swap["tx_id"]].append(swap)

    mapped_swaps_all = defaultdict(list)
    for swap in swaps:
        tx_id = swap["tx_id"]
        if tx_id not in mapped_swaps_jupiter:
            mapped_swaps_all[tx_id].append(swap)

    mapped_swaps = mapped_swaps_all | mapped_swaps_jupiter

    populate_swaps_data(mapped_swaps)
    combined_swaps = [swap for _swaps in mapped_swaps.values() for swap in _swaps]

    bots = 0
    scammers = 0
    for swap in combined_swaps:
        if swap.get("is_part_of_transaction_with_mt_3_swappers"):
            scammers += 1
        if swap.get("is_part_of_arbitrage_swap_event"):
            bots += 1

    logger.info(
        f"\nСвапов - Всего: {len(swaps)} | Юпитер: {len(swaps_jupiter)}"
        f"\nТранзакций - Всего: {len(mapped_swaps)} | Без юпитера: {len(mapped_swaps_all)} | Юпитер: {len(mapped_swaps_jupiter)}"
        # f"\nТранзакций юпитера которых нет в общих: {len(test)}"
        f"\nСвапов суммарно: {len(combined_swaps)}"
        f"\nБот свапов: {bots} | Скам. свапов: {scammers}"
    )

    return combined_swaps


def filter_swaps(
    swaps: list,
    blacklisted_tokens: List[str] | None = None,
) -> list[dict]:
    """Отфильтровывает неподходящие активности"""
    blacklisted_tokens = blacklisted_tokens or []

    def _filter(swap):
        swap_from_mint = swap.get("swap_from_mint")
        swap_to_mint = swap.get("swap_to_mint")
        if not (swap_from_mint == SOL_ADDRESS or swap_to_mint == SOL_ADDRESS):
            return False
        elif swap_from_mint == SOL_ADDRESS:
            if swap_to_mint in blacklisted_tokens:
                return False
        elif swap_to_mint == SOL_ADDRESS:
            if swap_from_mint in blacklisted_tokens:
                return False
        return True

    filtered_swaps = list(filter(_filter, swaps))
    return filtered_swaps


def extract_data_from_swaps(
    swaps: list,
    sol_prices: dict,
    blacklisted_tokens: List[str] | None = None,
) -> Tuple[List[Wallet], List[Token], List[Swap]]:
    """Извлечение и создание обьектов кошельков, токенов и активностей из полученных swaps"""
    filtered_swaps = filter_swaps(swaps, blacklisted_tokens)
    activities = []
    wallets = []
    tokens = []
    unique_wallet_addresses = set()
    unique_token_addresses = set()

    for swap in filtered_swaps:
        if not all([swap["swapper"], swap["tx_id"]]):
            continue
        wallet_address = swap["swapper"]
        if swap["swap_from_mint"] == SOL_ADDRESS:
            token_address = swap["swap_to_mint"]
            event_type = "buy"
            quote_amount = Decimal(str(swap["swap_from_amount"]))
            token_amount = Decimal(str(swap["swap_to_amount"]))
        else:
            token_address = swap["swap_from_mint"]
            event_type = "sell"
            quote_amount = Decimal(str(swap["swap_to_amount"]))
            token_amount = Decimal(str(swap["swap_from_amount"]))
        iso_string = swap["block_timestamp"]
        # Убираем 'Z' (если она есть) для совместимости с fromisoformat
        iso_string = iso_string.replace("Z", "+00:00")
        # Преобразуем строку в объект datetime
        swap_datetime = datetime.fromisoformat(iso_string)
        swap_minute = swap_datetime.replace(second=0, microsecond=0)

        sol_price = sol_prices[swap_minute]
        cost_usd = Decimal(str(quote_amount * sol_price))
        price_usd = Decimal(str(cost_usd / token_amount)) if token_amount else None

        activity = Swap(
            id=uuid.uuid1(),
            tx_hash=swap["tx_id"],
            block_id=swap["block_id"],
            timestamp=swap_datetime.timestamp(),
            event_type=event_type,
            quote_amount=quote_amount,
            token_amount=token_amount,
            cost_usd=cost_usd,
            price_usd=price_usd,
            is_part_of_transaction_with_mt_3_swappers=swap.get(
                "is_part_of_transaction_with_mt_3_swappers",
                False,
            ),
            is_part_of_arbitrage_swap_event=swap.get(
                "is_part_of_arbitrage_swap_event",
                False,
            ),
        )
        activity.wallet_address = wallet_address
        activity.token_address = token_address
        activities.append(activity)

        if wallet_address not in unique_wallet_addresses:
            unique_wallet_addresses.add(wallet_address)
            wallet = Wallet(address=wallet_address)
            wallets.append(wallet)
        if token_address not in unique_token_addresses:
            unique_token_addresses.add(token_address)
            token = Token(
                address=token_address,
            )
            tokens.append(token)
    return wallets, tokens, activities


def map_data_by_wallets(
    wallets_map: dict,
    tokens_map: dict,
    activities: List[Swap],
) -> dict:
    """Маппинг данных по кошелькам"""

    # {
    #     wallet_id: {
    #         'wallet': wallet_object,  # Объект кошелька
    #         'tokens': {
    #             token_id: {
    #                 'token': token_object,  # Объект токена
    #                 'activities': [activity_1, activity_2, ...],  # Список активностей для этого токена
    #                 'stats': stats_object  # Статистика для токена (если есть)
    #             },
    #             ...
    #         },
    #     },
    #     ...
    # }
    def default_token_structure():
        return {
            "token": None,
            "activities": [],
            "stats": None,
        }  # Словарь с токеном и списком активностей

    def default_wallet_structure():
        return {
            "wallet": None,
            "tokens": defaultdict(default_token_structure),
        }

    mapped_data = defaultdict(default_wallet_structure)

    for activity in activities:
        wallet = wallets_map[activity.wallet_address]
        token = tokens_map[activity.token_address]
        activity.wallet_id = wallet.id
        activity.token_id = token.id
        mapped_data[wallet.id]["wallet"] = wallet
        mapped_data[wallet.id]["tokens"][token.id]["token"] = token
        mapped_data[wallet.id]["tokens"][token.id]["activities"].append(activity)

    return mapped_data


def calculate_token_stats(
    token_data: dict,
) -> None:
    """Пересчитывает статистику для связки кошелька с токеном"""
    stats = token_data["stats"]
    token_activities = token_data["activities"]

    for activity in token_activities:
        if activity.event_type == "buy":
            stats.total_buys_count += 1
            stats.total_buy_amount_usd += activity.cost_usd if activity.cost_usd else 0
            stats.total_buy_amount_token += activity.token_amount if activity.token_amount else 0
            if not stats.first_buy_timestamp or (activity.timestamp <= stats.first_buy_timestamp):
                stats.first_buy_timestamp = activity.timestamp
                stats.first_buy_price_usd = activity.price_usd
        else:
            stats.total_sales_count += 1
            stats.total_sell_amount_usd += activity.cost_usd if activity.cost_usd else 0
            stats.total_sell_amount_token += activity.token_amount if activity.token_amount else 0
            if not stats.first_sell_timestamp or (activity.timestamp <= stats.first_sell_timestamp):
                stats.first_sell_timestamp = activity.timestamp
                stats.first_sell_price_usd = activity.price_usd

        if not stats.last_activity_timestamp or (activity.timestamp >= stats.last_activity_timestamp):
            stats.last_activity_timestamp = activity.timestamp

        if activity.is_part_of_transaction_with_mt_3_swappers:
            stats.total_swaps_from_txs_with_mt_3_swappers += 1
        if activity.is_part_of_arbitrage_swap_event:
            stats.total_swaps_from_arbitrage_swap_events += 1

    if (
        stats.first_buy_timestamp
        and stats.first_sell_timestamp
        and (stats.first_buy_timestamp <= stats.first_sell_timestamp)
    ):
        stats.first_buy_sell_duration = stats.first_sell_timestamp - stats.first_buy_timestamp
    if stats.total_buys_count > 0:
        stats.total_profit_usd = stats.total_sell_amount_usd - stats.total_buy_amount_usd
        stats.total_profit_percent = (
            round(
                stats.total_profit_usd / stats.total_buy_amount_usd * 100,
                2,
            )
            if not stats.total_buy_amount_usd == 0
            else None
        )

    stats.updated_at = datetime.now(pytz.timezone("Europe/Moscow"))


def recalculate_wallet_token_stats(wallets_dict):
    new_count = 0
    for wallet_data in wallets_dict.values():
        wallet = wallet_data["wallet"]
        tokens = wallet_data["tokens"]
        for token_data in tokens.values():
            token = token_data["token"]
            stats = token_data["stats"]
            # Создаем новый обьект токен-статистики если его не существует для токена
            if not stats:
                new_count += 1
                stats = token_data["stats"] = WalletToken(
                    token_id=token.id,
                    wallet_id=wallet.id,
                )
            calculate_token_stats(token_data)
    logger.info(f"Новых токен-статс {new_count}")


def split_time_range(start_time, end_time, parts):
    """Разбивает временной промежуток на равные части"""
    delta = (end_time - start_time) / parts
    intervals = [
        (
            start_time + i * delta,
            start_time + (i + 1) * delta,
        )
        for i in range(parts - 1)
    ]
    # Добавляем последний интервал, чтобы гарантировать точное совпадение с end_time
    intervals.append(
        (
            start_time + (parts - 1) * delta,
            end_time,
        )
    )
    return intervals


def get_non_existing_wallet_relations(wallets):
    wallet_details = []
    wallet_stats_7d = []
    wallet_stats_30d = []
    wallet_stats_all = []

    for wallet in wallets:
        if wallet.details is None:
            _wallet_details = WalletDetail(
                wallet_id=wallet.id,
            )
            wallet_details.append(_wallet_details)
        if wallet.stats_7d is None:
            _wallet_stats_7d = WalletStatistic7d(
                wallet_id=wallet.id,
            )
            wallet_stats_7d.append(_wallet_stats_7d)
        if wallet.stats_30d is None:
            _wallet_stats_30d = WalletStatistic30d(
                wallet_id=wallet.id,
            )
            wallet_stats_30d.append(_wallet_stats_30d)
        if wallet.stats_all is None:
            _wallet_stats_all = WalletStatisticAll(
                wallet_id=wallet.id,
            )
            wallet_stats_all.append(_wallet_stats_all)

    return (
        wallet_details,
        wallet_stats_7d,
        wallet_stats_30d,
        wallet_stats_all,
    )


def calculate_last_wallet_activity_timestamps(
    wallets: list,
    mapped_data: dict,
):
    for wallet in wallets:
        wallet_data = mapped_data[wallet.id]
        # Собираем все активности для кошелька
        all_activities = [
            activity for token_data in wallet_data["tokens"].values() for activity in token_data["activities"]
        ]
        last_activity_timestamp = (
            datetime.fromtimestamp(
                max(
                    all_activities,
                    key=lambda x: x.timestamp,
                ).timestamp,
                tz=timezone.utc,
            )
            if all_activities
            else None
        )
        last_activity_timestamp_in_db = wallet.last_activity_timestamp
        if last_activity_timestamp and (
            last_activity_timestamp_in_db is None or last_activity_timestamp > last_activity_timestamp_in_db
        ):
            wallet.last_activity_timestamp = last_activity_timestamp
