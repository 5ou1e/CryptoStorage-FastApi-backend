import asyncio
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timedelta, timezone
from functools import partial
from pathlib import Path

import pytz
from flipside.errors.query_run_errors import (
    QueryRunCancelledError,
    QueryRunExecutionError,
)
from pydantic.error_wrappers import ValidationError
from tortoise import Tortoise

from src.infra.db.setup import init_db_async

from . import db_utils, utils
from .flipside_queries import get_swaps, get_swaps_jupiter
from .logger import logger

BASE_DIR = Path(__file__).parent

with open(BASE_DIR / "tokens_blacklist.txt", "r") as file:
    BLACKLISTED_TOKENS = [line.strip() for line in file.readlines()]


def fetch_data_for_period(start_time, end_time, flipside_apikey, is_jupiter=False):
    offset = 0
    limit = 100000
    all_swaps = []
    all_count = 0
    stop = False
    while not stop:
        if is_jupiter:
            logger.info(
                f"Собираем данные Jupiter за {start_time} - {end_time} | offset: {offset}"
            )
            swaps, count = get_swaps_jupiter(
                flipside_apikey, start_time, end_time, offset=offset, limit=limit
            )
        else:
            logger.info(
                f"Собираем данные за {start_time} - {end_time} | offset: {offset}"
            )
            swaps, count = get_swaps(
                flipside_apikey, start_time, end_time, offset=offset, limit=limit
            )

        all_swaps.extend(swaps)
        all_count += count
        if count < limit:
            stop = True
        else:
            offset += limit

    return all_swaps, all_count, is_jupiter


async def process_wallet_tokens(
    mapped_data: dict,
    token_wallet_list: list,
    chunks_count: int = 10,
):
    # Получаем записи WalletToken из БД -> пересчитываем -> импортируем в бд обратно
    wallet_tokens = await db_utils.load_wallet_tokens(
        token_wallet_list, chunks_count=chunks_count
    )
    logger.info(f"WalletToken-статистики загружены")

    for stats in wallet_tokens:
        mapped_data[stats.wallet_id]["tokens"][stats.token_id]["stats"] = stats

    calculations.recalculate_wallet_token_stats(mapped_data)
    logger.info(f"WalletToken-статистики пересчитаны")

    wt_stats = [
        token_data["stats"]
        for wallet_data in mapped_data.values()
        for token_data in wallet_data["tokens"].values()
    ]

    await db_utils.import_wallet_tokens(wt_stats, chunks_count=chunks_count)
    logger.info(f"WalletToken-статистики импортированы")
    return wt_stats


async def import_data_to_db(swaps_all, swaps_jupiter, sol_prices, start_time, end_time):
    # async with in_transaction() as conn:
    logger.info(f"Начинаем импорт данных за {start_time} - {end_time}")
    start = datetime.now()
    swaps = utils.combine_swaps(swaps_all, swaps_jupiter)
    wallets, tokens, activities = utils.extract_data_from_swaps(
        swaps, sol_prices, blacklisted_tokens=BLACKLISTED_TOKENS
    )

    logger.info(f"Время создания обьектов: {datetime.now() - start}")
    logger.info("Начинаем импорт чанками!")

    created_wallets, created_tokens = await asyncio.gather(
        db_utils.import_wallets(wallets), db_utils.import_tokens(tokens)
    )

    logger.info("Кошельки импортированы")
    logger.info("Токены импортированы")

    mapped_data = mappers.map_data_by_wallets(created_wallets, created_tokens, activities)

    # После полуения кошельков из БД пересчитываем последн. активность и обновляем
    utils.calculate_last_wallet_activity_timestamps(
        list(created_wallets.values()),
        mapped_data,
    )

    await db_utils.update_wallets(list(created_wallets.values()))
    logger.info("Кошельки обновлены")

    token_wallet_list = mappers.create_wallet_token_ids_list(activities)

    results = await asyncio.gather(
        db_utils.import_activities(activities),
        process_wallet_tokens(mapped_data, token_wallet_list),
    )
    logger.info(f"Активности импортированы")

    wallet_details, wallet_stats_7d, wallet_stats_30d, wallet_stats_all = (
        utils.get_non_existing_wallet_relations(created_wallets.values())
    )

    # Только после импорта всех активностей\статистик токенов импортируем связи кошелька
    await asyncio.gather(
        db_utils.create_wallet_statistics_7d(wallet_stats_7d),
        db_utils.create_wallet_statistics_30d(wallet_stats_30d),
        db_utils.create_wallet_statistics_all(wallet_stats_all),
    )
    await asyncio.gather(
        db_utils.create_wallet_details(wallet_details),
    )

    logger.info("WalletDetails импортированы")
    logger.info("WalletStatistic7d импортированы")
    logger.info("WalletStatisticAll импортированы")
    logger.info("WalletStatisticAll импортированы")

    wt_stats = results[1]
    swaps_count = len(swaps)
    wallets_count = len(wallets)
    tokens_count = len(tokens)
    activities_count = len(activities)
    wt_stats_count = len(wt_stats)
    wallet_details_count = len(wallet_details)
    logger.info(
        f"Импортировали данные за {start_time} - {end_time}"
        f"\nСвапов: {swaps_count}"
        f"\nСвапов после фильтра: {activities_count}"
        f"\nКошельков: {wallets_count}"
        f"\nDetails: {wallet_details_count}"
        f"\nТокенов: {tokens_count}"
        f"\nКошелек-токен стат.: {wt_stats_count}"
    )
    # await conn.rollback()


async def process_period(start_time, end_time, sol_prices, flipside_account):
    start_parsing = datetime.now()

    intervals = utils.split_time_range(start_time, end_time, 12)
    intervals_jupiter = utils.split_time_range(start_time, end_time, 4)

    swaps = []
    swaps_jupiter = []
    swaps_count = 0

    try:
        loop = asyncio.get_running_loop()
        with ProcessPoolExecutor(max_workers=16) as executor:
            # Создаем задачи для каждого интервала
            tasks = [
                loop.run_in_executor(
                    executor,
                    partial(
                        fetch_data_for_period, start, end, flipside_account.api_key
                    ),
                )
                for start, end in intervals
            ]
            tasks.extend(
                [
                    loop.run_in_executor(
                        executor,
                        partial(
                            fetch_data_for_period,
                            start,
                            end,
                            flipside_account.api_key,
                            is_jupiter=True,
                        ),
                    )
                    for start, end in intervals_jupiter
                ]
            )
            # Ждем завершения всех задач
            results = await asyncio.gather(*tasks)

    except ValidationError as e:
        logger.error(e)
        raise ValueError("Flipside Error")

    for _swaps, _swaps_count, is_jupiter in results:
        if is_jupiter:
            swaps_jupiter.extend(_swaps)
        else:
            swaps.extend(_swaps)
        swaps_count += _swaps_count

    if swaps_count > 0 or len(swaps_jupiter) > 0:
        start_import = datetime.now()
        await import_data_to_db(swaps, swaps_jupiter, sol_prices, start_time, end_time)
        end_import = datetime.now()
        logger.info(
            f"\nВремя общee: {end_import - start_parsing} | Импорт: {end_import - start_import}"
        )
    else:
        logger.info(f"За период {start_time} - {end_time} нету свапов!")


async def _process():
    try:
        flipside_config = await db_utils.get_flipside_config()
        if not flipside_config:
            logger.error(f"Не найден FlipsideCrypto-конфиг в БД")
            return

        start_time, end_time = get_start_end_time(flipside_config)
        logger.info(f"{start_time} | {end_time}")

        current_time = start_time
        while current_time < end_time:
            next_time = current_time + timedelta(
                minutes=60
            )  # Максимальный диапазон за запрос
            if next_time > end_time:
                next_time = end_time

            flipside_account = await db_utils.get_flipside_account()
            if not flipside_account:
                logger.error(f"Нету активных аккаунтов FlipsideCrypto в БД")
                return

            sol_prices = await db_utils.get_sol_prices(
                minute_from=current_time - timedelta(minutes=1),
                minute_to=next_time + timedelta(minutes=1),
            )
            if not sol_prices.get(next_time):
                logger.error(f"Ошибка: Нету данных о цене соланы в {next_time}!")
                return

            try:
                await process_period(
                    current_time, next_time, sol_prices, flipside_account
                )
                await db_utils.update_flipside_config_swaps_parsed_untill(
                    flipside_config, parsed_untill=next_time
                )
                current_time = next_time
            except (QueryRunExecutionError, QueryRunCancelledError, ValueError) as e:
                if isinstance(e, ValueError) and "Flipside Error" not in str(e):
                    raise e
                logger.error(type(e))
                logger.error(f"Меняем учетку Flipside - {str(e)}")
                await db_utils.set_flipside_account_inactive(flipside_account)
    except Exception as e:
        logger.error(f"Error: {e}")
        raise e


def get_start_end_time(flipside_config):
    utc_tz = pytz.timezone("UTC")
    last_tx_inserted_timestamp = flipside_config.swaps_parsed_untill_inserted_timestamp
    start_time = last_tx_inserted_timestamp.astimezone(utc_tz)
    end_time = datetime.now(utc_tz) - timedelta(minutes=1440)
    return start_time, end_time


# def get_start_end_time(flipside_config):
#     utc_tz = pytz.timezone('UTC')
#     _start_time = "2025-02-18 10:45:00"
#     start_time = utc_tz.localize(datetime.strptime(_start_time, "%Y-%m-%d %H:%M:%S"))
#     _end_time = "2025-02-18 10:45:00"
#     end_time = utc_tz.localize(datetime.strptime(_end_time, "%Y-%m-%d %H:%M:%S"))
#     end_time = end_time.replace(second=0, microsecond=0)
#     return start_time, end_time


async def process():
    await init_db_async()
    try:
        await _process()
    finally:
        await Tortoise.close_connections()
