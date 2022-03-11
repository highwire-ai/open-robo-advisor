# Open Robo-Advisor :robot:

Open Robo-Advisor is a flexible robo-advisor library written in Python.

* **Works with any asset**\
  ETFs, mutual funds, stocks, crypto, bonds, ...
* **Supports asset targeting**\
  10% USD, 20% VXUS, 70% VTI
* **Understands asset class targeting**\
  5% cash, 5% crypto, 20% foreign stock, 70% domestic stock
* **Handles multiple currencies**\
  USD, CAD, BTC, ...
* **Complete transaction history**\
  In-memory double-entry bookkeeping ledger

## Quickstart

Start by creating a portfolio and adding an account to it.

```
portfolio = Portfolio()
account = portfolio.open_account('My Fidelity Account')
```

Set up the initial assets. In this case, our Fidelity account receives $2000, and buys 4.5177 shares of VTI.

```
account.deposit(2000)

account.buy(
    symbol='VTI',
    shares=Decimal('4.5177'),
    amount=1000,
    fees=Decimal('9.95'),
)
```

The account has $990.05 in cash and 4.5177 shares of VTI at this point. The $990.05 is what's left when you deposit $2000, then buy $1000 worth of VTI and pay a $9.95 fee.

We need to define asset targets so the advisor knows the desired balance. Since we're going to use SimpleAdvisor, we set the targets for assets (USD, VTI, VEA) rather than asset classes (cash, US stock, foregin emerging market).

```
account_targets = {
    'My Fidelity Account': {
        Currency('USD'): Decimal('0.02'),
        Security('VTI'): Decimal('0.45'),
        Security('VEA'): Decimal('0.15'),
        Security('VWO'): Decimal('0.15'),
        Security('VIG'): Decimal('0.09'),
        Security('VTEB'): Decimal('0.14'),
    }
}
```

SimpleAdvisor nees to know what assets are currently worth. Define a map from assets to current prices.

```
quotes = {
    Currency('USD'): 1,
    Security('VTI'): Decimal('221.17'),
    Security('VEA'): Decimal('47.79'),
    Security('VWO'): Decimal('47.82'),
    Security('VIG'): Decimal('158.08'),
    Security('VTEB'): Decimal('53.24'),
}
```

Instantiate the advisor and get its suggestions. This example uses SimpleAdvisor, which will always 

```
advisor = SimpleAdvisor(
    portfolio=portfolio,
    account_targets=account_targets,
    quotes=quotes,
)

suggestions = advisor.get_suggestions()
```

Suggestions look like this:

```
{'My Fidelity Account': [Sell(asset_type=Currency('USD'), amount=Decimal('950.26540582')),
                         Sell(asset_type=Security('VTI'), amount=Decimal('104.02633995')),
                         Buy(asset_type=Security('VEA'), amount=Decimal('298.38445635')),
                         Buy(asset_type=Security('VWO'), amount=Decimal('298.38445635')),
                         Buy(asset_type=Security('VIG'), amount=Decimal('179.03067381')),
                         Buy(asset_type=Security('VTEB'), amount=Decimal('278.49215926'))]}
```

## Advisors

Open Robo-Advisor has two advisors:

* [SimpleAdvisor](https://github.com/highwire-ai/open-robo-advisor/blob/main/src/openroboadvisor/advisor/simple_advisor.py)
* [AssetClassAdvisor](https://github.com/highwire-ai/open-robo-advisor/blob/main/src/openroboadvisor/advisor/asset_class_advisor.py)

### SimpleAdvisor

SimpleAdvisor allows developers to set percentage-based targets for specific assets (e.g. 10% USD, 20% VXUS and 70% VTI). SimpleAdvisor compares the asset targets to the holdings in a portfolio, and make trade suggestions to rebalance.

### AssetClassAdvisor

AssetClassAdvisor is similar to SimpleAdvisor, except that percent-based targets are set for asset classes (e.g. 10% cash, 20% foreign stock, 70% US stock). AssetClassAdvisor compares the asset class targets to the holdings in a portfolio and makes trade suggestions to keep the portfolio in balance.

AssetClassAdvisor also understands the concept of preferred assets for each asset class. A portfolio might have VTI and ITOT in it. In such a case, the advisor can be made to understand that these are both US stock assets; new purchase suggestions will use VTI and ITOT will be liquidated before VTI if a sale is suggested.
