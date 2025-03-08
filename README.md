```
├── application
│   ├── __init__.py
│   ├── common
│   │   ├── __init__.py
│   │   ├── dto.py
│   │   └── utils.py
│   ├── etl
│   │   ├── __init__.py
│   │   ├── block_id_updater.py
│   │   ├── sol_prices_collector.py
│   │   ├── swaps_parser
│   │   │   ├── __init__.py
│   │   │   ├── calculations.py
│   │   │   ├── config.py
│   │   │   ├── db_utils.py
│   │   │   ├── flipside_queries.py
│   │   │   ├── logger.py
│   │   │   ├── mappers.py
│   │   │   ├── parser.py
│   │   │   ├── rollback.py
│   │   │   ├── run.py
│   │   │   ├── tokens_blacklist.txt
│   │   │   └── utils.py
│   │   ├── swaps_parser(fast_unsafe)
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── db_utils.py
│   │   │   ├── flipside_queries.py
│   │   │   ├── logger.py
│   │   │   ├── otkat.py
│   │   │   ├── parser.py
│   │   │   ├── run.py
│   │   │   ├── tokens_blacklist.txt
│   │   │   └── utils.py
│   │   ├── tg_wallets_sender.py
│   │   ├── tokens_metadata_parser.py
│   │   ├── utils.py
│   │   ├── wallet_statistic_buygt15k_update_manager.py
│   │   └── wallet_statistic_update_manager.py
│   ├── exceptions.py
│   ├── interfaces
│   │   ├── __init__.py
│   │   ├── repositories
│   │   │   ├── __init__.py
│   │   │   ├── generic_repository.py
│   │   │   ├── swap.py
│   │   │   ├── token.py
│   │   │   ├── user.py
│   │   │   └── wallet.py
│   │   └── uow.py
│   ├── token
│   │   ├── __init__.py
│   │   ├── dto.py
│   │   ├── exceptions.py
│   │   └── queries
│   │       ├── __init__.py
│   │       ├── get_token_by_address.py
│   │       └── get_tokens.py
│   ├── user
│   │   ├── __init__.py
│   │   ├── dto.py
│   │   ├── exceptions.py
│   │   └── service.py
│   └── wallet
│       ├── __init__.py
│       ├── dto
│       │   ├── __init__.py
│       │   ├── wallet.py
│       │   ├── wallet_activity.py
│       │   ├── wallet_details.py
│       │   ├── wallet_related_wallet.py
│       │   ├── wallet_stats.py
│       │   └── wallet_token.py
│       ├── exceptions.py
│       ├── queries
│       │   ├── __init__.py
│       │   ├── get_wallet_activities.py
│       │   ├── get_wallet_by_address.py
│       │   ├── get_wallet_related_wallets.py
│       │   ├── get_wallet_tokens.py
│       │   └── get_wallets.py
│       └── wallet.py
├── domain
│   ├── __init__.py
│   └── entities
│       ├── __init__.py
│       ├── base_entity.py
│       ├── swap.py
│       ├── token.py
│       ├── user.py
│       └── wallet.py
├── infra
│   ├── __init__.py
│   ├── celery
│   │   ├── __init__.py
│   │   ├── setup.py
│   │   ├── task_logger.py
│   │   └── tasks.py
│   ├── db
│   │   ├── __init__.py
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── sqlalchemy
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   ├── external_services.py
│   │   │   │   ├── swap.py
│   │   │   │   ├── token.py
│   │   │   │   ├── user.py
│   │   │   │   └── wallet.py
│   │   │   └── tortoise
│   │   │       ├── __init__.py
│   │   │       ├── common.py
│   │   │       ├── external_services.py
│   │   │       ├── swap.py
│   │   │       ├── token.py
│   │   │       ├── user.py
│   │   │       ├── utils.py
│   │   │       └── wallet.py
│   │   ├── queries.py
│   │   ├── repositories
│   │   │   ├── __init__.py
│   │   │   ├── sqlalchemy
│   │   │   │   ├── __init__.py
│   │   │   │   ├── generic_repository.py
│   │   │   │   ├── swap.py
│   │   │   │   ├── token.py
│   │   │   │   ├── user.py
│   │   │   │   └── wallet.py
│   │   │   └── tortoise
│   │   │       ├── __init__.py
│   │   │       ├── generic_repository.py
│   │   │       ├── swap.py
│   │   │       ├── token.py
│   │   │       ├── user.py
│   │   │       └── wallet.py
│   │   ├── setup.py
│   │   ├── setup_tortoise.py
│   │   ├── uow
│   │   │   ├── __init__.py
│   │   │   └── sqlachemy.py
│   │   └── utils.py
│   └── processors
│       ├── __init__.py
│       └── password_hasher_argon.py
├── presentation
│   ├── __init__.py
│   └── api
│       ├── __init__.py
│       ├── builder.py
│       ├── dependencies
│       │   ├── __init__.py
│       │   ├── auth.py
│       │   ├── repositories.py
│       │   └── services.py
│       ├── endpoints
│       │   ├── __init__.py
│       │   ├── common
│       │   │   ├── __init__.py
│       │   │   ├── docs.py
│       │   │   └── root.py
│       │   └── v1
│       │       ├── __init__.py
│       │       ├── auth.py
│       │       ├── test.py
│       │       ├── token.py
│       │       └── wallet.py
│       ├── exceptions.py
│       ├── main.py
│       ├── middlewares.py
│       ├── routers.py
│       └── schemas
│           ├── __init__.py
│           └── response.py
└── settings
    ├── __init__.py
    ├── config.py
    └── logging.py
```
