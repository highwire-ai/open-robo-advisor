from datetime import date
from decimal import Decimal
from openroboadvisor.ledger import Ledger
from openroboadvisor.ledger.account import AccountType
from openroboadvisor.ledger.asset import Currency, Security
from openroboadvisor.ledger.entry import OpenAccount
from openroboadvisor.portfolio.account import Account, EXTERNAL_BANK_ID
from pytest import raises


def test_get_balances_before_account_open() -> None:
    account_id = 'test'
    ledger = Ledger()
    account = Account(
        account_id=account_id,
        ledger=ledger,
    )

    with raises(AssertionError, match=r"No ledger account found.*"):
        account.get_balances()

def test_get_balances_empty() -> None:
    account_id = 'test'
    ledger = Ledger()
    account = Account(
        account_id=account_id,
        ledger=ledger,
    )
    ledger.record(OpenAccount(
        account_id=account_id,
        account_type=AccountType.BROKERAGE,
        entry_date=date(2022, 1, 1)
    ))

    balances = account.get_balances()
    assert balances.subaccounts == {}, "Expected empty subaccounts"
    assert balances.cash == {}, "Expected no cash"
    assert balances.securities == {}, "Expected no securities"

def test_basic_account_functionality() -> None:
    account_id = 'test'
    ledger = Ledger()
    account = Account(
        account_id=account_id,
        ledger=ledger,
    )
    ledger.record(OpenAccount(
        account_id=account_id,
        account_type=AccountType.BROKERAGE,
        entry_date=date(2022, 1, 1)
    ))
    ledger.record(OpenAccount(
        account_id=EXTERNAL_BANK_ID,
        account_type=AccountType.BROKERAGE,
        entry_date=date(2022, 1, 1)
    ))

    account.deposit(1000)

    balances = account.get_balances()
    assert balances.cash == {
        Currency('USD'): Decimal(1000),
    }
    assert balances.securities == {}
    assert account.get_fees() == {}

    account.buy(
        symbol='AAPL',
        shares=1,
        amount=Decimal('151.32'),
        fees=Decimal('9.95'),
    )

    balances = account.get_balances()
    assert balances.cash == {
        Currency('USD'): Decimal('838.73'),
    }
    assert balances.securities == {
        Security('AAPL', ): Decimal(1),
    }
    assert account.get_fees() == {
        Currency('USD'): Decimal('9.95'),
    }

    account.sell(
        symbol='AAPL',
        shares=1,
        amount=Decimal(200),
        fees=10,
    )

    balances = account.get_balances()
    assert balances.cash == {
        Currency('USD'): Decimal('1028.73'),
    }
    assert balances.securities == {
        Security('AAPL', ): Decimal(0),
    }
    assert account.get_fees() == {
        Currency('USD'): Decimal('19.95'),
    }

    account.withdraw(
        amount=Decimal('1028.73'),
    )


    balances = account.get_balances()
    assert balances.cash == {
        Currency('USD'): Decimal(0),
    }
    assert balances.securities == {
        Security('AAPL', ): Decimal(0),
    }
    assert account.get_fees() == {
        Currency('USD'): Decimal('19.95'),
    }
