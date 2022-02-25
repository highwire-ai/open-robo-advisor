from decimal import Decimal
from openroboadvisor.portfolio import Portfolio
from openroboadvisor.ledger.asset import Currency, Security


USD = Currency('USD')
SPY = Security('SPY')


def test_basic_portfolio() -> None:
    portfolio = Portfolio()
    account = portfolio.open_account('My Fidelity Account')

    account.deposit(2000)

    balances = account.get_balances()
    assert balances.cash.get(USD) == 2000, "Expected a $2000 deposit."
    assert len(balances.securities) == 0, "Found securities, but haven't purchased any yet."

    account.buy(
        symbol='SPY',
        shares=Decimal('2.0933'),
        amount=1000,
        fees=Decimal('9.95')
    )

    balances = account.get_balances()
    assert balances.cash.get(USD) == Decimal('990.05'), "Expected a $990.05 after buying stock."
    assert balances.securities.get(SPY) == Decimal('2.0933'), "Expected to have shares of SPY."

    account.sell(
        symbol='SPY',
        shares=Decimal('2.0933'),
        amount=2000,
        fees=Decimal('9.95')
    )


    balances = account.get_balances()
    assert balances.cash.get(USD) == Decimal('2980.10'), "Expected a $2980.10 after selling SPY for a gain."
    assert balances.securities.get(SPY) == 0, "All SPY shares were sold, but quantity isn't empty."
