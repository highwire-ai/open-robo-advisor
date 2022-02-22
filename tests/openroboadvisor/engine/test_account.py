from datetime import date
from decimal import Decimal
from openroboadvisor.engine.account import Account
from openroboadvisor.engine.transaction import Deposit, Buy, Sell


def test_single_account() -> None:
    transactions = [
        Deposit(
            amount=2000,
            transfer_date=date(2022, 1, 1),
            settlement_date=date(2022, 1, 3)),
        Buy(
            symbol='SPY',
            amount=1000,
            quantity=Decimal('2.3209'),
            price=Decimal('426.58'),
            fees=Decimal('9.95'),
            trade_date=date(2022, 1, 3),
            settlement_date=date(2022, 1, 4)),
        Sell(
            symbol='SPY',
            amount=Decimal('416.37'),
            quantity=Decimal(1),
            price=Decimal('406.42'),
            fees=Decimal('9.95'),
            trade_date=date(2022, 1, 5),
            settlement_date=date(2022, 1, 7)),
    ]

    account = Account("My Brokerage", transactions)

    jan1 = account.holdings(as_of=date(2022, 1, 1))
    assert jan1.as_of == date(2022, 1, 1)
    assert jan1.current_cash == 2000
    assert jan1.settled_cash == 0
    assert len(jan1.current_holdings) == 0
    assert len(jan1.settled_holdings) == 0

    jan2 = account.holdings(as_of=date(2022, 1, 2))
    assert jan2.as_of == date(2022, 1, 2)
    assert jan2.current_cash == 2000
    assert jan2.settled_cash == 0
    assert len(jan2.current_holdings) == 0
    assert len(jan2.settled_holdings) == 0

    jan3 = account.holdings(as_of=date(2022, 1, 3))
    assert jan3.as_of == date(2022, 1, 3)
    assert jan3.current_cash == 1000
    assert jan3.settled_cash == 2000
    assert len(jan3.current_holdings) == 1
    assert jan3.current_holdings['SPY'] == Decimal('2.3209')
    assert len(jan3.settled_holdings) == 0

    jan4 = account.holdings(as_of=date(2022, 1, 4))
    assert jan4.current_cash == 1000
    assert jan4.settled_cash == 1000
    assert len(jan4.current_holdings) == 1
    assert jan4.current_holdings['SPY'] == Decimal('2.3209')
    assert len(jan4.settled_holdings) == 1
    assert jan4.settled_holdings['SPY'] == Decimal('2.3209')

    jan5 = account.holdings(as_of=date(2022, 1, 5))
    assert jan5.current_cash == Decimal('1406.42')
    assert jan5.settled_cash == 1000
    assert len(jan5.current_holdings) == 1
    assert jan5.current_holdings['SPY'] == Decimal('1.3209')
    assert len(jan5.settled_holdings) == 1
    assert jan5.settled_holdings['SPY'] == Decimal('2.3209')

    jan7 = account.holdings(as_of=date(2022, 1, 7))
    assert jan7.current_cash == Decimal('1406.42')
    assert jan7.settled_cash == Decimal('1406.42')
    assert len(jan7.current_holdings) == 1
    assert jan7.current_holdings['SPY'] == Decimal('1.3209')
    assert len(jan7.settled_holdings) == 1
    assert jan7.settled_holdings['SPY'] == Decimal('1.3209')
