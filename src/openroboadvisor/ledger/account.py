from .asset import AssetType, Currency, Security
from decimal import Decimal
from enum import Enum, auto
from typing import List


class AccountType(Enum):
    UNKNOWN = -1
    CHECKING = auto()
    SAVINGS = auto()
    BROKERAGE = auto()
    TYPE_401A = auto()
    TYPE_401K = auto()
    TYPE_403B = auto()
    TYPE_457B = auto()
    TYPE_529 = auto()
    IRA = auto()
    ROTH_IRA = auto()
    ROTH_401k = auto()
    UGMA = auto()
    UTMA = auto()


class Subaccount:
    def __init__(
        self,
        subaccount_id: str,
        assets: dict[AssetType, Decimal] | None = None,
    ) -> None:
        self.subaccount_id = subaccount_id
        self.assets: dict[AssetType, Decimal] = assets or {}

    def inc(self, quantity: Decimal | int, asset_type: AssetType) -> None:
        old_asset_quantity = self.assets.get(asset_type, 0)
        self.assets[asset_type] = old_asset_quantity + quantity
        return old_asset_quantity

    def get_assets(
        self,
        types: set[AssetType] = {Currency, Security},
    ) -> dict[AssetType, Decimal]:
        return {
            k: v for k, v in self.assets.items() if type(k) in types
        }

    def __eq__(self, another) -> None:
        return \
            isinstance(another, type(self)) and \
            self.subaccount_id == another.subaccount_id and \
            self.assets == another.assets

    def __repr__(self) -> str:
        return f'{type(self).__name__}({repr(self.subaccount_id)}, {repr(self.assets)})'


class Account:
    def __init__(
        self,
        account_id: str,
        account_type: AccountType,
    ) -> None:
        self.account_id = account_id
        self.account_type = account_type
        self.subaccounts: dict[str, Subaccount] = {}

    def subaccount(self, subaccount_id: str) -> Subaccount:
        return self.subaccounts.setdefault(
            subaccount_id,
            Subaccount(subaccount_id)
        )
