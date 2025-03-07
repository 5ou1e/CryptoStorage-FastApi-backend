from src.application.common.dto import Pagination
from src.application.common.utils import create_paginated_response
from src.application.interfaces.repositories.swap import BaseSwapRepository
from src.application.interfaces.repositories.wallet import BaseWalletRepository
from src.application.interfaces.uow import BaseUnitOfWork
from src.application.wallet.dto import (
    GetWalletActivitiesFilters,
    WalletActivityDTO,
    WalletActivityPageDTO,
)
from src.application.wallet.exceptions import WalletNotFoundException


class GetWalletActivitiesHandler:
    def __init__(
        self,
        wallet_repository: BaseWalletRepository,
        swap_repository: BaseSwapRepository,
    ) -> None:
        self._wallet_repository = wallet_repository
        self._swap_repository = swap_repository

    async def __call__(
        self,
        address,
        pagination: Pagination,
        filters: GetWalletActivitiesFilters,
    ) -> WalletActivityPageDTO:
        wallet = await self._wallet_repository.get_by_address(address=address)
        if not wallet:
            raise WalletNotFoundException(address)
        filter_by = filters.model_dump(exclude_none=True)
        filter_by["wallet_id"] = wallet.id
        activities = await self._swap_repository.get_page(
            page=pagination.page,
            per_page=pagination.per_page,
        )
        total_count = await self._swap_repository.get_count(
            # filter_by=filter_by
        )
        wallet_activities_response = [
            WalletActivityDTO.from_orm(activity) for activity in activities
        ]
        return create_paginated_response(
            data=wallet_activities_response,
            total_count=total_count,
            pagination=pagination,
            response_model=WalletActivityPageDTO,
            data_field="activities",
        )
