from decimal import Decimal
from openroboadvisor.advisor.asset_class_advisor import AssetClassAdvisor
from openroboadvisor.advisor.suggestion import Buy, Sell
from openroboadvisor.ledger.asset import Currency, Security
from openroboadvisor.portfolio import Portfolio


ACCOUNT_ID = 'My Fidelity Account'
CASH = 'Cash'
US_STOCKS = 'US Stocks'
FOREIGN_STOCKS = 'Foreign Stocks'
EMERGING_MARKETS = 'Emerging Markets'
DIVIDEND_STOCKS = 'Dividend Stocks'
MUNICIPAL_BONDS = 'Municipal Bonds'
PREFERRED_ASSETS = [
    Currency('USD'),
    Security('VTI'),
    Security('VEA'),
    Security('VWO'),
    Security('VIG'),
    Security('VTEB'),
]
ASSET_CLASSES = {
    Currency('USD'): CASH,
    Security('VTI'): US_STOCKS,
    Security('ITOT'): US_STOCKS,
    Security('VEA'): FOREIGN_STOCKS,
    Security('VWO'): EMERGING_MARKETS,
    Security('VIG'): DIVIDEND_STOCKS,
    Security('VTEB'): MUNICIPAL_BONDS,
}

def test_asset_class_advisor() -> None:
    portfolio = Portfolio()
    account = portfolio.open_account(ACCOUNT_ID)

    account.deposit(2000)
    account.buy(
        symbol='SPY',
        shares=Decimal('2.0933'),
        amount=1000,
        fees=Decimal('9.95')
    )
    account.buy(
        symbol='ITOT',
        shares=Decimal('1'),
        amount=Decimal('95.51'),
        fees=Decimal('9.95')
    )

    balances = account.get_balances()

    assert len(balances.cash) == 1, "Expected just USD"
    assert len(balances.securities) == 2, "Expected VTI and ITOT"
    assert balances.cash.get(Currency('USD')) == Decimal('884.59'), "Expected 884.59 USD cash balance"
    assert balances.securities.get(Security('SPY')) == Decimal('2.0933'), "Expected 4.5177 SPY shares"
    assert balances.securities.get(Security('ITOT')) == Decimal(1), "Expected 1 ITOT share"
    assert account.get_fees().get(Currency('USD')) == Decimal('19.9'), "Expected 19.90 in fees"

    account_targets = {
        ACCOUNT_ID: {
            CASH: Decimal('0.02'),
            US_STOCKS: Decimal('0.45'),
            FOREIGN_STOCKS: Decimal('0.15'),
            EMERGING_MARKETS: Decimal('0.15'),
            DIVIDEND_STOCKS: Decimal('0.09'),
            MUNICIPAL_BONDS: Decimal('0.14'),
        }
    }

    quotes = {
        Currency('USD'): 1,
        Security('VTI'): Decimal('221.17'),
        Security('VEA'): Decimal('47.79'),
        Security('VWO'): Decimal('47.82'),
        Security('VIG'): Decimal('158.08'),
        Security('VTEB'): Decimal('53.24'),
        Security('SPY'): Decimal('472.96'),
        Security('ITOT'): Decimal('96.51'),
    }

    advisor = AssetClassAdvisor(
        portfolio=portfolio,
        preferred_assets=PREFERRED_ASSETS,
        asset_classes=ASSET_CLASSES,
        account_targets=account_targets,
        quotes=quotes,
    )

    suggestions = advisor.get_suggestions().get(ACCOUNT_ID)
    sorted_suggestions = sorted(suggestions, key=lambda s: s.asset_type.symbol)

    assert sorted_suggestions == [
        Sell(asset_type=Security('SPY'), amount=Decimal('990.047168')),
        Sell(asset_type=Currency('USD'), amount=Decimal('845.16705664')),
        Buy(asset_type=Security('VEA'), amount=Decimal('295.67207520')),
        Buy(asset_type=Security('VIG'), amount=Decimal('177.40324512')),
        Buy(asset_type=Security('VTEB'), amount=Decimal('275.96060352')),
        Buy(asset_type=Security('VTI'), amount=Decimal('790.50622560')),
        Buy(asset_type=Security('VWO'), amount=Decimal('295.67207520')),
    ]
