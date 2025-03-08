src/
├── application/
│   ├── common/
│   │   ├── dto.py
│   │   └── utils.py
│   ├── interfaces/
│   │   ├── repositories/
│   │   │   └── uow.py
│   ├── wallet/
│   │   ├── dto/
│   │   ├── queries/
│   │   │   ├── exceptions.py
│   │   │   └── wallet.py
│   │   └── exceptions.py
│   ├── user/
├── domain/
│   ├── entities/
│   │   ├── base_entity.py
│   │   ├── user.py
│   │   ├── wallet.py
├── infra/
│   ├── celery/
│   │   ├── tasks/
│   │   │   └── setup.py
│   ├── db/
│   │   ├── models/
│   │   │   ├── sqlalchemy/
│   │   │   ├── tortoise/
│   ├── repositories/
│   │   ├── sqlalchemy/
│   │   ├── tortoise/
│   ├── uow/
│   │   ├── queries.py
│   │   ├── setup.py
│   │   ├── setup_tortoise.py
│   │   ├── utils.py
│   ├── processors/
│   ├── scripts/
├── presentation/
│   ├── api/
│   │   ├── dependencies/
│   │   │   ├── auth.py
│   │   │   ├── repositories.py
│   │   │   ├── services.py
│   │   ├── endpoints/
│   │   │   ├── common/
│   │   │   ├── v1/
│   │   │   │   ├── auth.py
│   │   │   │   ├── user.py
│   │   │   │   ├── wallet.py
│   ├── schemas/
│   │   ├── response.py
│   │   ├── builder.py
│   │   ├── exceptions.py
│   │   ├── main.py
│   │   ├── middlewares.py
│   │   ├── routers.py
