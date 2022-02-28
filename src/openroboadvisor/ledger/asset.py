from datetime import date
from decimal import Decimal
from typing import Tuple

class AssetType:
    def __init__(
        self,
        symbol: str
    ) -> None:
        self.symbol = symbol

    def __eq__(self, another) -> None:
        return (
            isinstance(another, type(self)) and
            self.symbol == another.symbol
        )

    def __hash__(self) -> None:
        return hash(self.symbol)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({repr(self.symbol)})'


Price = Tuple[Decimal, AssetType]


class Currency(AssetType):
    pass

class Security(AssetType):
    def __init__(
        self,
        symbol: str,
        lot: str | None = None,
    ) -> None:
        super().__init__(symbol)
        self.lot = lot

    def without_lot(self) -> 'Security':
        return Security(self.symbol)

    def __eq__(self, another):
        return (
            super().__eq__(another) and
            self.lot == another.lot,
        )

    def __hash__(self):
        return hash((
            super().__hash__(),
            self.lot,
        ))

    def __repr__(self) -> str:
        if self.lot:
            return f"{super().__repr__()}[lot={repr(self.lot)}]"
        else:
            return super().__repr__()
