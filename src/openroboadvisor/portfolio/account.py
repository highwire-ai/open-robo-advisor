from datetime import date
from decimal import Decimal
from openroboadvisor.ledger import Ledger
from openroboadvisor.ledger.account import Subaccount
from openroboadvisor.ledger.asset import AssetType, Currency, Security
from openroboadvisor.ledger.entry import Transaction, TransactionLeg


EXTERNAL_BANK_ID = '__external_bank'
PENDING_SUBACCOUNT_ID = 'pending'
SETTLED_SUBACCOUNT_ID = 'settled'
FEES_SUBACCOUNT_ID = 'fees'


class Balances:
    def __init__(
        self,
        subaccounts: dict[str, Subaccount],
        include_pending: bool,
        include_lots: bool,
    ) -> None:
        # TODO handle include_lots
        self.subaccounts = subaccounts
        self.include_pending = include_pending
        self.include_lots = include_lots
        self.cash: dict[Currency, Decimal] = self.get_asset_quantities(Currency)
        self.securities: dict[Security, Decimal] = self.get_asset_quantities(Security)

    # TODO this method should probably be templated to 'T extends AssetType'
    def get_asset_quantities(self, asset_type: AssetType) -> dict[AssetType, Decimal]:
        settled = self.subaccounts.get(
            SETTLED_SUBACCOUNT_ID,
            Subaccount(SETTLED_SUBACCOUNT_ID),
        ).get_assets({asset_type})

        if self.include_pending:
            pending = self.subaccounts.get(
                PENDING_SUBACCOUNT_ID,
                Subaccount(PENDING_SUBACCOUNT_ID),
            ).get_assets({asset_type})

            for pending_asset, pending_quantity in pending.items():
                settled_quantity = settled.get(pending_asset, 0)
                total_quantity = settled_quantity + pending_quantity
                settled[pending_asset] = total_quantity

        return settled

    def get_asset_amounts(self, asset_type: AssetType, quotes: dict[AssetType, Decimal]) -> dict[AssetType, Decimal]:
        asset_quantities = self.get_asset_quantities(asset_type)
        asset_amounts: dict[AssetType, Decmal] = {}

        for asset_type, quantity in asset_quantities.items():
            quote = quotes.get(asset_type)
            # TODO assert quote
            asset_amounts[asset_type] = quote * quantity

        return asset_amounts

    def total(self, quotes: dict[AssetType, Decimal]) -> Decimal:
        total_balance = Decimal(0)

        for asset, quantity in (self.cash | self.securities).items():
            quote = quotes.get(asset.without_lot()) if isinstance(asset, Security) else quotes.get(asset)
            assert quote, f"Unable to find quote (asset={asset})"
            total_balance += quote * quantity

        return total_balance


class Account:
    def __init__(
        self,
        account_id: str,
        ledger: Ledger,
    ) -> None:
        self.account_id = account_id
        self.ledger = ledger

    def get_balances(
        self,
        include_pending: bool = True,
        include_lots: bool = False,
    ) -> Balances:
        ledger_account = self.ledger.get_account(self.account_id)
        assert ledger_account, \
            f"No ledger account found (account_id='{self.account_id}')"
        return Balances(
            ledger_account.subaccounts,
            include_pending,
            include_lots,
        )

    def get_fees(self) -> dict[AssetType, Decimal]:
        account = self.ledger.get_account(self.account_id)
        subaccount = account.subaccounts.get(FEES_SUBACCOUNT_ID)
        return subaccount.assets if subaccount else {}

    def deposit(
        self,
        amount: Decimal | int,
        currency: str = 'USD',
        transfer_date: date | None = None,
        settlement_date: date | None = None,
    ) -> None:
        resolved_amount = Decimal(amount)
        resolved_currency = Currency(currency)
        resolved_transfer_date = transfer_date or date.today()
        resolved_settlement_date = settlement_date or resolved_transfer_date

        self.ledger.record(
            Transaction(
                TransactionLeg(
                    account_id=EXTERNAL_BANK_ID,
                    subaccount_id=PENDING_SUBACCOUNT_ID,
                    asset_type=resolved_currency,
                    quantity=-resolved_amount,
                ),
                TransactionLeg(
                    account_id=self.account_id,
                    subaccount_id=PENDING_SUBACCOUNT_ID,
                    asset_type=resolved_currency,
                    quantity=resolved_amount
                ),
                entry_date=resolved_transfer_date,
            ),
            Transaction(
                TransactionLeg(
                    account_id=self.account_id,
                    subaccount_id=PENDING_SUBACCOUNT_ID,
                    asset_type=resolved_currency,
                    quantity=-resolved_amount,
                ),
                TransactionLeg(
                    account_id=self.account_id,
                    subaccount_id=SETTLED_SUBACCOUNT_ID,
                    asset_type=resolved_currency,
                    quantity=resolved_amount,
                ),
                entry_date=resolved_settlement_date,
            ),
        )

    def withdraw(
        self,
        amount: Decimal | int,
        currency: str = 'USD',
        transfer_date: date | None = None,
        settlement_date: date | None = None,
    ) -> None:
        resolved_amount = Decimal(amount)
        resolved_currency = Currency(currency)
        resolved_transfer_date = transfer_date or date.today()
        resolved_settlement_date = settlement_date or resolved_transfer_date

        self.ledger.record(
            Transaction(
                TransactionLeg(
                    account_id=self.account_id,
                    subaccount_id=PENDING_SUBACCOUNT_ID,
                    asset_type=resolved_currency,
                    quantity=-resolved_amount
                ),
                TransactionLeg(
                    account_id=EXTERNAL_BANK_ID,
                    subaccount_id=PENDING_SUBACCOUNT_ID,
                    asset_type=resolved_currency,
                    quantity=resolved_amount,
                ),
                entry_date=resolved_transfer_date,
            ),
            Transaction(
                TransactionLeg(
                    account_id=self.account_id,
                    subaccount_id=SETTLED_SUBACCOUNT_ID,
                    asset_type=resolved_currency,
                    quantity=-resolved_amount,
                ),
                TransactionLeg(
                    account_id=self.account_id,
                    subaccount_id=PENDING_SUBACCOUNT_ID,
                    asset_type=resolved_currency,
                    quantity=resolved_amount,
                ),
                entry_date=resolved_settlement_date,
            ),
        )

    def buy(
        self,
        symbol: str,
        shares: Decimal | int,
        amount: Decimal | int,
        fees: Decimal | int = 0,
        currency: str = 'USD',
        trade_date: date | None = None,
        settlement_date: date | None = None,
        lot: str | None = None,
    ) -> None:
        resolved_security = Security(symbol, lot)
        resolved_shares = Decimal(shares)
        resolved_amount = Decimal(amount)
        resolved_fees = Decimal(fees)
        resolved_currency = Currency(currency)
        resolved_trade_date = trade_date or date.today()
        resolved_settlement_date = settlement_date or resolved_trade_date

        self.ledger.record(
            Transaction(
                TransactionLeg(
                    account_id=self.account_id,
                    subaccount_id=PENDING_SUBACCOUNT_ID,
                    asset_type=resolved_currency,
                    quantity=-(resolved_amount + resolved_fees),
                ),
                TransactionLeg(
                    account_id=self.account_id,
                    subaccount_id=FEES_SUBACCOUNT_ID,
                    asset_type=resolved_currency,
                    quantity=resolved_fees,
                ),
                TransactionLeg(
                    account_id=self.account_id,
                    subaccount_id=PENDING_SUBACCOUNT_ID,
                    asset_type=resolved_security,
                    quantity=resolved_shares,
                    cost=(resolved_amount, resolved_currency)
                ),
                entry_date=resolved_trade_date,
            ),
            Transaction(
                TransactionLeg(
                    account_id=self.account_id,
                    subaccount_id=SETTLED_SUBACCOUNT_ID,
                    asset_type=resolved_currency,
                    quantity=-(resolved_amount + resolved_fees),
                ),
                TransactionLeg(
                    account_id=self.account_id,
                    subaccount_id=PENDING_SUBACCOUNT_ID,
                    asset_type=resolved_currency,
                    quantity=resolved_amount + resolved_fees,
                ),
                TransactionLeg(
                    account_id=self.account_id,
                    subaccount_id=PENDING_SUBACCOUNT_ID,
                    asset_type=resolved_security,
                    quantity=-resolved_shares,
                ),
                TransactionLeg(
                    account_id=self.account_id,
                    subaccount_id=SETTLED_SUBACCOUNT_ID,
                    asset_type=resolved_security,
                    quantity=resolved_shares,
                ),
                entry_date=resolved_settlement_date,
            ),
        )

    def sell(
        self,
        symbol: str,
        shares: Decimal | int,
        amount: Decimal | int,
        fees: Decimal | int = 0,
        currency: str = 'USD',
        trade_date: date | None = None,
        settlement_date: date | None = None,
        lot: str | None = None,
    ) -> None:
        resolved_security = Security(symbol, lot)
        resolved_shares = Decimal(shares)
        resolved_amount = Decimal(amount)
        resolved_fees = Decimal(fees)
        resolved_currency = Currency(currency)
        resolved_trade_date = trade_date or date.today()
        resolved_settlement_date = settlement_date or resolved_trade_date

        self.ledger.record(
            Transaction(
                TransactionLeg(
                    account_id=self.account_id,
                    subaccount_id=PENDING_SUBACCOUNT_ID,
                    asset_type=resolved_currency,
                    quantity=resolved_amount - resolved_fees,
                ),
                TransactionLeg(
                    account_id=self.account_id,
                    subaccount_id=FEES_SUBACCOUNT_ID,
                    asset_type=resolved_currency,
                    quantity=resolved_fees,
                ),
                TransactionLeg(
                    account_id=self.account_id,
                    subaccount_id=PENDING_SUBACCOUNT_ID,
                    asset_type=resolved_security,
                    quantity=-resolved_shares,
                    cost=(-amount, resolved_currency)
                ),
                entry_date=resolved_trade_date,
            ),
            Transaction(
                TransactionLeg(
                    account_id=self.account_id,
                    subaccount_id=PENDING_SUBACCOUNT_ID,
                    asset_type=resolved_currency,
                    quantity=-(resolved_amount - resolved_fees),
                ),
                TransactionLeg(
                    account_id=self.account_id,
                    subaccount_id=SETTLED_SUBACCOUNT_ID,
                    asset_type=resolved_currency,
                    quantity=resolved_amount - resolved_fees,
                ),
                TransactionLeg(
                    account_id=self.account_id,
                    subaccount_id=SETTLED_SUBACCOUNT_ID,
                    asset_type=resolved_security,
                    quantity=-resolved_shares,
                ),
                TransactionLeg(
                    account_id=self.account_id,
                    subaccount_id=PENDING_SUBACCOUNT_ID,
                    asset_type=resolved_security,
                    quantity=resolved_shares,
                ),
                entry_date=resolved_settlement_date,
            ),
        )
