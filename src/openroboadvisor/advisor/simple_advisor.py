from .base_advisor import BaseAdvisor
from .suggestion import Buy, Sell, Suggestion
from decimal import Decimal
from openroboadvisor.ledger.asset import AssetType, Currency, Security
from openroboadvisor.portfolio import Portfolio
from typing import List


class SimpleAdvisor(BaseAdvisor):
    def __init__(
        self,
        portfolio: Portfolio,
        account_targets: dict[str, dict[AssetType, Decimal]],
        quotes: dict[AssetType, Decimal],
    ) -> None:
        super().__init__(
            portfolio=portfolio
        )
        self.portfolio = portfolio
        self.account_targets = account_targets
        self.quotes = quotes

    def get_account_suggestions(self, account_id: str) -> List[Suggestion]:
        suggestions = []
        account = self.portfolio.accounts.get(account_id)
        assert account, f"Unable to find account (account_id={account_id})"

        targets = self.account_targets.get(account_id)
        assert targets, f"Unable to find targets (account_id={account_id})"

        balances = account.get_balances()
        total_balance = balances.total(self.quotes)
        asset_amounts = (
            balances.get_asset_amounts(Currency, self.quotes) |
            balances.get_asset_amounts(Security, self.quotes)
        )

        for asset_type, current_amount in asset_amounts.items():
            target_percent = targets.get(asset_type, Decimal(0))
            target_amount = total_balance * target_percent
            imbalance = target_amount - current_amount

            if imbalance > 0:
                suggestions.append(Buy(asset_type, imbalance))
            elif imbalance < 0:
                suggestions.append(Sell(asset_type, -imbalance))

        for asset_type, target_percent in targets.items():
            if asset_type not in asset_amounts:
                target_amount = total_balance * target_percent
                suggestions.append(Buy(asset_type, target_amount))

        return suggestions
