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


class Balance:
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
        self.cash: dict[Currency, Decimal] = self.calculate_asset_balance(Currency)
        self.securities: dict[Security, Decimal] = self.calculate_asset_balance(Security)

    def calculate_asset_balance(self, asset_type: AssetType) -> dict[Currency, Decimal]:
        settled = self.subaccounts[SETTLED_SUBACCOUNT_ID].get_assets({asset_type})

        if self.include_pending:
            pending = self.subaccounts[PENDING_SUBACCOUNT_ID].get_assets({asset_type})

            for pending_asset, pending_quantity in pending.items():
                settled_quantity = settled.get(pending_asset, 0)
                total_quantity = settled_quantity + pending_quantity
                settled[pending_asset] = total_quantity

        return settled


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
    ) -> Balance:
        ledger_account = self.ledger.get_account(self.account_id)
        return Balance(
            ledger_account.subaccounts,
            include_pending,
            include_lots,
        )

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
