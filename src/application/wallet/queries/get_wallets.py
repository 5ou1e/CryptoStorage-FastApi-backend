from src.application.common.dto import Pagination
from src.application.common.utils import (
    create_paginated_response,
)
from src.application.interfaces.repositories.wallet import (
    BaseWalletRepository,
)
from src.application.wallet.dto import (
    GetWalletsFilters,
    WalletDetailedDTO,
    WalletsPageDTO,
)


class GetWalletsHandler:
    def __init__(
        self,
        wallet_repository: BaseWalletRepository,
    ) -> None:
        self._wallet_repository = wallet_repository

    async def __call__(
        self,
        pagination: Pagination,
        filters: GetWalletsFilters,
    ) -> WalletsPageDTO:
        wallets = await self._wallet_repository.get_page(
            page=pagination.page, page_size=pagination.page_size, filters=filters
        )
        total_count = await self._wallet_repository.get_count(filters=filters)
        wallets_response = [WalletDetailedDTO.from_orm(wallet) for wallet in wallets]
        return create_paginated_response(
            data=wallets_response,
            total_count=total_count,
            pagination=pagination,
            response_model=WalletsPageDTO,
            data_field="wallets",
        )
