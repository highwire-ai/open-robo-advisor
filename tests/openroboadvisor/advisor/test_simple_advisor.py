from decimal import Decimal
from openroboadvisor.advisor.simple_advisor import SimpleAdvisor
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

    # TODO assert account state
    """
    Account state:

    USD=884.59
    VTI=1000 (4.5177 shares)
    ITOT=95.51 (1 share)
    fees=19.9
    """

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

    suggestions = advisor.get_suggestions()

    # TODO assert suggestions and balances
    """
    Total balance: 1,980.279709

    USD=884.59
    VTI=999.179709 (4.5177 shares)
    ITOT=96.51 (1 share)

    Target state:

    USD=39.60559418 
    VTI=891.12586905
    VEA=297.04195635
    VWO=297.04195635
    VIG=178.22517381
    VTEB=277.23915926
    """

    import pprint
    pprint.pprint(suggestions)
    """
    {'My Fidelity Account': [Sell(asset_type=Currency('USD'), amount=Decimal('844.98440582')),
                          Sell(asset_type=Security('VTI'), amount=Decimal('108.05383995')),
                          Sell(asset_type=Security('ITOT'), amount=Decimal('96.510000')),
                          Buy(asset_type=Security('VEA'), amount=Decimal('297.04195635')),
                          Buy(asset_type=Security('VWO'), amount=Decimal('297.04195635')),
                          Buy(asset_type=Security('VIG'), amount=Decimal('178.22517381')),
                          Buy(asset_type=Security('VTEB'), amount=Decimal('277.23915926'))]}
    """
