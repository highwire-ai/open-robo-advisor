from .account import Account, AccountType
from .asset import AssetType, Price
from datetime import date
from decimal import Decimal


class Entry:
    def __init__(
        self,
        entry_date: date
    ) -> None:
        self.entry_date = entry_date

    def validate(self, accounts: dict[str, Account]) -> None:
        pass

# TODO Should we just have one SetStatus entry instead of open/close?
class OpenAccount(Entry):
    def __init__(
        self,
        entry_date: date,
        account_id: str,
        account_type: AccountType,
    ) -> None:
        self.entry_date = entry_date
        self.account_id = account_id
        self.account_type = account_type

    def validate(self, accounts: dict[str, Account]) -> None:
        assert self.account_id not in accounts, (
            "Can't open an account when it's already open "
            f"(account_id='{self.account_id}')"
        )


class CloseAccount(Entry):
    def __init__(
        self,
        entry_date: date,
        account_id: str,
    ) -> None:
        self.entry_date = entry_date
        self.account_id = account_id

    def validate(self, accounts: dict[str, Account]) -> None:
        # TODO validate account is not already closed
        pass


class TransactionLeg:
    def __init__(
        self,
        account_id: str,
        subaccount_id: str,
        asset_type: AssetType,
        quantity: Decimal | int,
        cost: Price | None = None
    ) -> None:
        self.account_id = account_id
        self.subaccount_id = subaccount_id
        self.asset_type = asset_type
        self.quantity = quantity
        self.cost = cost


class Transaction(Entry):
    def __init__(
        self,
        *legs: TransactionLeg,
        entry_date: date,
    ) -> None:
        self.entry_date = entry_date
        self.legs: List[TransactionLeg] = legs

    def validate(self, accounts: dict[str, Account]) -> None:
        self.validate_accounts(accounts)
        self.validate_quantities()

    def validate_accounts(self, accounts: dict[str, Account]) -> None:
        for leg in self.legs:
            assert leg.account_id in accounts, (
                "Transaction references missing account "
                f"(account_id='{leg.account_id}')"
            )

    def validate_quantities(self) -> None:
        current_quantities: dict[AssetType, Decimal] = {}

        for leg in self.legs:
            quantity, asset_type = leg.cost if leg.cost else (leg.quantity, leg.asset_type)
            current_quantity = current_quantities.get(asset_type, 0)
            current_quantities[asset_type] = current_quantity + quantity
            print(current_quantities)

        for asset_type, quantity in current_quantities.items():
            assert quantity == 0, (
                "Transaction has an imbalance "
                f"(asset_type='{asset_type}', quantity={quantity})"
            )
