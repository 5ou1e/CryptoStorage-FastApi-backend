from src.application.interfaces.repositories.token import (
    BaseTokenPriceRepository,
    BaseTokenRepository,
)
from src.infra.db.models.tortoise.token import Token, TokenPrice

from .generic_repository import TortoiseGenericRepository


class TortoiseTokenRepository(TortoiseGenericRepository, BaseTokenRepository):
    model = Token

    # noinspection PyMethodMayBeStatic
    async def get_by_address(self, address: str) -> Token | None:
        return await Token.filter(address=address).first()


class TortoiseTokenPriceRepository(TortoiseGenericRepository, BaseTokenPriceRepository):
    model = TokenPrice
