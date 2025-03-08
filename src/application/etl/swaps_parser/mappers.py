from collections import defaultdict
from typing import List

from src.infra.db.models.tortoise import Swap


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


def map_objects_by_address(objects):
    mapped = {}
    for obj in objects:
        mapped[obj.address] = obj
    return mapped
