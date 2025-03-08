from typing import Any, Optional

from fastapi import APIRouter
from fastapi_filter.contrib.sqlalchemy import (
    Filter,
)

from src.application.wallet.queries.get_wallet_by_address import (
    GetWalletByAddressHandler,
)
from src.infra.db.models.sqlalchemy import (
    User,
    Wallet,
    WalletDetail,
)
from src.infra.db.repositories.sqlalchemy import (
    SQLAlchemyWalletRepository,
)
from src.infra.db.setup import (
    AsyncSessionLocal,
    get_db_session,
)
from src.presentation.api.schemas.response import (
    ApiResponse,
)

router = APIRouter(prefix="/test", tags=["Test endpoints"])


class WalletDetailFilter(Filter):
    is_bot: Optional[bool] = None

    class Constants(Filter.Constants):
        model = WalletDetail


class WalletFilter(Filter):
    address: Optional[str] = None
    # details: Optional[WalletDetailFilter] = FilterDepends(with_prefix("details", WalletDetailFilter))
    details__is_bot: Optional[bool]

    class Constants(Filter.Constants):
        model = Wallet


@router.get("/test", response_model=Any)
async def test() -> Any:
    session = get_db_session()
    async with get_db_session() as session:
        repo = SQLAlchemyWalletRepository(session)
        service = GetWalletByAddressHandler(repo)
        result = await service(address="12312312")
        return ApiResponse(result=result)
