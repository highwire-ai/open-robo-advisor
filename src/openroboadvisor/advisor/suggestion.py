from decimal import Decimal
from openroboadvisor.ledger.asset import AssetType


class Suggestion:
    def __init__(
        self,
        asset_type: AssetType,
        amount: Decimal
    ) -> None:
        self.asset_type = asset_type
        self.amount = amount

    def __eq__(self, another) -> None:
        return \
            isinstance(another, type(self)) and \
            self.asset_type == another.asset_type and \
            self.amount == another.amount

    def __hash__(self) -> None:
        return hash((self.asset_type, self.amount))

    def __repr__(self) -> str:
        return f'{type(self).__name__}(asset_type={repr(self.asset_type)}, amount={repr(self.amount)})'


class Buy(Suggestion):
    pass

class Sell(Suggestion):
    pass
