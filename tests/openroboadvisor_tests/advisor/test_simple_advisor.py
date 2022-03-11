from decimal import Decimal
from openroboadvisor.advisor.simple_advisor import SimpleAdvisor
from openroboadvisor.advisor.suggestion import Buy, Sell
from openroboadvisor.ledger.asset import Currency, Security
from openroboadvisor.portfolio import Portfolio


ACCOUNT_ID = 'My Fidelity Account'


def test_simple_advisor():
    portfolio = Portfolio()
    account = portfolio.open_account(ACCOUNT_ID)

    account.deposit(2000)

    account.buy(
        symbol='VTI',
        shares=Decimal('4.5177'),
        amount=1000,
        fees=Decimal('9.95'),
    )

    account.buy(
        symbol='ITOT',
        shares=Decimal('1'),
        amount=Decimal('95.51'),
        fees=Decimal('9.95'),
    )

    balances = account.get_balances()

    assert len(balances.cash) == 1, "Expected just USD"
    assert len(balances.securities) == 2, "Expected VTI and ITOT"
    assert balances.cash.get(Currency('USD')) == Decimal('884.59'), "Expected 884.59 USD cash balance"
    assert balances.securities.get(Security('VTI')) == Decimal('4.5177'), "Expected 4.5177 VTI shares"
    assert balances.securities.get(Security('ITOT')) == Decimal(1), "Expected 1 ITOT share"
    assert account.get_fees().get(Currency('USD')) == Decimal('19.9'), "Expected 19.90 in fees"

    account_targets = {
        ACCOUNT_ID: {
            Currency('USD'): Decimal('0.02'),
            Security('VTI'): Decimal('0.45'),
            Security('VEA'): Decimal('0.15'),
            Security('VWO'): Decimal('0.15'),
            Security('VIG'): Decimal('0.09'),
            Security('VTEB'): Decimal('0.14'),
        }
    }

    quotes = {
        Currency('USD'): 1,
        Security('VTI'): Decimal('221.17'),
        Security('VEA'): Decimal('47.79'),
        Security('VWO'): Decimal('47.82'),
        Security('VIG'): Decimal('158.08'),
        Security('VTEB'): Decimal('53.24'),
        Security('ITOT'): Decimal('96.51'),
    }

    advisor = SimpleAdvisor(
        portfolio=portfolio,
        account_targets=account_targets,
        quotes=quotes,
    )

    suggestions = advisor.get_suggestions().get(ACCOUNT_ID)
    sorted_suggestions = sorted(suggestions, key=lambda s: s.asset_type.symbol)

    assert sorted_suggestions == [
        Sell(asset_type=Security('ITOT'), amount=Decimal('96.510000')),
        Sell(asset_type=Currency('USD'), amount=Decimal('844.98440582')),
        Buy(asset_type=Security('VEA'), amount=Decimal('297.04195635')),
        Buy(asset_type=Security('VIG'), amount=Decimal('178.22517381')),
        Buy(asset_type=Security('VTEB'), amount=Decimal('277.23915926')),
        Sell(asset_type=Security('VTI'), amount=Decimal('108.05383995')),
        Buy(asset_type=Security('VWO'), amount=Decimal('297.04195635')),
    ]
