from .tasks import (
    collect_sol_prices_task,
    parse_tokens_metadata_task,
    send_wallets_in_tg_task,
    update_single_wallet_statistics_task,
    update_wallet_statistics_buy_price_gt_15k_task,
    update_wallet_statistics_task,
)

__all__ = [
    "collect_sol_prices_task",
    "update_wallet_statistics_task",
    "update_single_wallet_statistics_task",
    "update_wallet_statistics_buy_price_gt_15k_task",
    "parse_tokens_metadata_task",
    "send_wallets_in_tg_task",
]
