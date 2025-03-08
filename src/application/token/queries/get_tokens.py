from src.application.common.dto import Pagination
from src.application.common.utils import (
    create_paginated_response,
)
from src.application.interfaces.repositories.token import (
    BaseTokenRepository,
)
from src.application.token.dto import (
    GetTokensFilters,
    TokenDTO,
    TokensPageDTO,
)


class GetTokensHandler:
    def __init__(
        self,
        token_repository: BaseTokenRepository,
    ):
        self.token_repository = token_repository

    async def __call__(
        self,
        pagination: Pagination,
        filters: GetTokensFilters,
    ) -> TokensPageDTO:
        filter_by = filters.model_dump()
        tokens = await self.token_repository.get_page(
            page=pagination.page,
            page_size=pagination.page_size,
            # filter_by=filter_by,
        )
        total_count = await self.token_repository.get_count()
        tokens_response = [TokenDTO.from_orm(token) for token in tokens]
        return create_paginated_response(
            data=tokens_response,
            total_count=total_count,
            pagination=pagination,
            response_model=TokensPageDTO,
            data_field="tokens",
        )
