# Open Robo-Advisor :robot:

Open Robo-Advisor (ORA) is a flexible robo-advisor library written in Python.

## Quickstart

## Advisors

ORA currently ships with two advisors:

* SimpleAdvisor
* AssetClassAdvisor

SimpleAdvisor allows developers to set percentage-based targets for specific assets (e.g. 10% USD, 20% VXUS and 70% VTI). SimpleAdvisor compares the asset targets to the holdings in a portfolio, and make trade suggestions to rebalance.

AssetClassAdvisor is similar to SimpleAdvisor, except that percent-based targets are set for asset classes (e.g. 10% cash, 20% foreign stock, 70% US stock). AssetClassAdvisor compares the asset class targets to the holdings in a portfolio and makes trade suggestions to keep the portfolio in balance. AssetClassAdvisor also understands the concept of preferred assets for each asset class. For example, a portfolio might have VTI and ITOT in it. In such a case, the advisor can be made to understand that these are both US stock assets; new purchase suggestions will use VTI and ITOT will be liquidated before VTI if a sale is suggested.
