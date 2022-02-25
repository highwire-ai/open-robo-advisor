from datetime import date
from decimal import Decimal
from openroboadvisor.ledger import Ledger
from openroboadvisor.ledger.asset import Currency, Security
from openroboadvisor.ledger.entry import OpenAccount, Transaction, TransactionLeg
from openroboadvisor.ledger.account import AccountType


def test_basic_ledger() -> None:
    trade_date = date(2022, 1, 3)
    settlement_date = date(2022, 1, 5)
    bank_account_id = 'External Bank'
    brokerage_account_id = 'My Fidelity Brokerage'
    ledger = Ledger()

    ledger.record(
        # Open external checking
        OpenAccount(
            account_id=bank_account_id,
            account_type=AccountType.CHECKING,
            entry_date=date(2022, 1, 3),
        ),
        # Open internal Fidelity brokerage
        OpenAccount(
            account_id=brokerage_account_id,
            account_type=AccountType.BROKERAGE,
            entry_date=date(2022, 1, 3),
        ),
        # Deposit money into brokerage
        Transaction(
            TransactionLeg(
                account_id=bank_account_id,
                subaccount_id='pending',
                asset_type=Currency('USD'),
                quantity=-2000,
            ),
            TransactionLeg(
                account_id=brokerage_account_id,
                subaccount_id='pending',
                asset_type=Currency('USD'),
                quantity=2000
            ),
            entry_date=date(2022, 1, 3),
        ),
        # Settle money in brokerage
        Transaction(
            TransactionLeg(
                account_id=brokerage_account_id,
                subaccount_id='pending',
                asset_type=Currency('USD'),
                quantity=-2000,
            ),
            TransactionLeg(
                account_id=brokerage_account_id,
                subaccount_id='settled',
                asset_type=Currency('USD'),
                quantity=2000,
            ),
            entry_date=date(2022, 1, 4),
        ),
        # Buy stock
        Transaction(
            TransactionLeg(
                account_id=brokerage_account_id,
                subaccount_id='pending',
                asset_type=Currency('USD'),
                quantity=Decimal('-1009.95'),
            ),
            TransactionLeg(
                account_id=brokerage_account_id,
                subaccount_id='fees',
                asset_type=Currency('USD'),
                quantity=Decimal('9.95'),
            ),
            TransactionLeg(
                account_id=brokerage_account_id,
                subaccount_id='pending',
                asset_type=Security('SPY'),
                quantity=Decimal('2.0933'),
                cost=(Decimal(1000), Currency('USD'))
            ),
            entry_date=date(2022, 1, 5),
        ),
        # Settle stock purchase
        Transaction(
            TransactionLeg(
                account_id=brokerage_account_id,
                subaccount_id='settled',
                asset_type=Currency('USD'),
                quantity=Decimal('-1009.95'),
            ),
            TransactionLeg(
                account_id=brokerage_account_id,
                subaccount_id='pending',
                asset_type=Currency('USD'),
                quantity=Decimal('1009.95'),
            ),
            TransactionLeg(
                account_id=brokerage_account_id,
                subaccount_id='pending',
                asset_type=Security('SPY'),
                quantity=Decimal('-2.0933'),
            ),
            TransactionLeg(
                account_id=brokerage_account_id,
                subaccount_id='settled',
                asset_type=Security('SPY'),
                quantity=Decimal('2.0933'),
            ),
            entry_date=date(2022, 1, 6),
        ),
        # Sell stock
        Transaction(
            TransactionLeg(
                account_id=brokerage_account_id,
                subaccount_id='pending',
                asset_type=Currency('USD'),
                quantity=Decimal('1990.05'),
            ),
            TransactionLeg(
                account_id=brokerage_account_id,
                subaccount_id='fees',
                asset_type=Currency('USD'),
                quantity=Decimal('9.95'),
            ),
            TransactionLeg(
                account_id=brokerage_account_id,
                subaccount_id='pending',
                asset_type=Security('SPY'),
                quantity=Decimal('-2.0933'),
                cost=(Decimal(-2000), Currency('USD'))
            ),
            entry_date=date(2022, 1, 7),
        ),
        # Settle stock sale
        Transaction(
            TransactionLeg(
                account_id=brokerage_account_id,
                subaccount_id='pending',
                asset_type=Currency('USD'),
                quantity=Decimal('-1990.05'),
            ),
            TransactionLeg(
                account_id=brokerage_account_id,
                subaccount_id='settled',
                asset_type=Currency('USD'),
                quantity=Decimal('1990.05'),
            ),
            TransactionLeg(
                account_id=brokerage_account_id,
                subaccount_id='settled',
                asset_type=Security('SPY'),
                quantity=Decimal('-2.0933'),
            ),
            TransactionLeg(
                account_id=brokerage_account_id,
                subaccount_id='pending',
                asset_type=Security('SPY'),
                quantity=Decimal('2.0933'),
            ),
            entry_date=date(2022, 1, 7),
        ),
    )
