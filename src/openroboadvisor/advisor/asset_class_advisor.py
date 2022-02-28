from .base_advisor import BaseAdvisor
from .suggestion import Buy, Sell, Suggestion
from decimal import Decimal
from openroboadvisor.ledger.asset import AssetType, Currency, Security
from openroboadvisor.portfolio import Portfolio
from openroboadvisor.portfolio.account import Account, Balances
from typing import List

class AssetClassAdvisor(BaseAdvisor):
    def __init__(
        self,
        portfolio: Portfolio,
        preferred_assets: List[AssetType],
        # TODO should we have a AssetClassProvider instead of a dict?
        asset_classes: dict[AssetType, str],
        account_targets: dict[str, dict[str, Decimal]],
        # TODO should we have a QuoteProvider instead of a dict?
        quotes: dict[AssetType, Decimal],
    ) -> None:
        self.portfolio = portfolio
        self.asset_classes = asset_classes
        self.account_targets = account_targets
        self.quotes = quotes
        self.preferred_assets = preferred_assets
        # TODO assert self.account_targets = 100%

    def get_account_suggestions(self, account_id: str) -> List[Suggestion]:
        account = self.portfolio.accounts.get(account_id)
        assert account, f"Unable to find account (account_id={account_id})"

        targets = self.account_targets.get(account_id)
        assert targets, f"Unable to find targets (account_id={account_id})"

        balances = account.get_balances()
        asset_class_imbalances = self._calculate_asset_class_imbalances(
            balances,
            targets
        )

        return self._calculate_suggestions(
            balances,
            asset_class_imbalances
        )

    def _calculate_asset_class_imbalances(
        self,
        balances: Balances,
        targets: dict[str, Decimal],
    ) -> dict[str, Decimal]:
        total_account_balance = balances.total(self.quotes)
        assets = balances.cash | balances.securities
        asset_class_values: dict[str, Decimal] = {}
        asset_class_imbalances: dict[str, Decimal] = {}

        for asset, quantity in assets.items():
            quote = self.quotes.get(asset)
            # TODO assert quote
            asset_class = self.asset_classes.get(asset)

            if asset_class:
                additional_value = quote * quantity
                current_value = asset_class_values.get(asset_class, Decimal(0))
                asset_class_values[asset_class] = current_value + additional_value

        for asset_class, target_percent in targets.items():
            asset_class_imbalances[asset_class] = (
                (target_percent * total_account_balance) - asset_class_values.get(asset_class, 0)
            )

        return asset_class_imbalances

    def _calculate_suggestions(
        self,
        balances: Balances,
        asset_class_imbalances: dict[str, Decimal]
    ) -> List[Suggestion]:
        classes_for_preferred_assets = {self.asset_classes.get(a): a for a in self.preferred_assets}
        assets = balances.cash | balances.securities
        suggestions = []

        for asset_class, imbalance_amount in asset_class_imbalances.items():
            preferred_asset = classes_for_preferred_assets.get(asset_class)
            # TODO assert preferred_asset

            if imbalance_amount > 0:
                suggestions.append(Buy(preferred_asset, imbalance_amount))
            else:
                #remaining_imbalance = imbalance_amount
                suggestions.extend(
                    self._calculate_assets_to_sell(
                        balances,
                        preferred_asset,
                        asset_class,
                        imbalance_amount
                    )
                )

                #suggestions.append(Sell(preferred_asset, -imbalance_amount))

        for asset, quantity in assets.items():
            asset_without_lot = asset.without_lot() if isinstance(asset, Security) else asset
            if asset_without_lot not in self.asset_classes:
                quote = self.quotes.get(asset_without_lot)
                # TODO assert quote
                suggestions.append(Sell(asset, quote * quantity))

        return suggestions

    def _calculate_assets_to_sell(
        self,
        balances: Balances,
        preferred_asset: AssetType,
        preferred_asset_class: str,
        imbalance_amount: Decimal,
    ) -> List[Sell]:
        suggestions = []
        remaining_imbalance = abs(imbalance_amount)
        asset_amounts = (
            balances.get_asset_amounts(Currency, self.quotes) |
            balances.get_asset_amounts(Security, self.quotes)
        )

        # Remove assets that aren't in the class we are looking at
        def asset_filter(asset_and_amount: (AssetType, Decimal)) -> bool:
            asset = asset_and_amount[0]
            asset_class = self.asset_classes.get(asset)
            # Exclude preferred asset so we can force it to the end after sorting
            return asset != preferred_asset and asset_class == preferred_asset_class

        assets_with_same_class = list(filter(
            asset_filter,
            asset_amounts.items())
        )

        # Sort by amount (low to high) to sell off smallest holdings first
        sorted_assets = sorted(
            assets_with_same_class,
            key=lambda a: a[1]
        )

        # Force preferred asset to be the last asset sold
        sorted_assets.append((preferred_asset, asset_amounts.get(preferred_asset)))

        for asset, amount in sorted_assets:
            sell_amount = min(amount, remaining_imbalance)
            remaining_imbalance -= sell_amount
            suggestions.append(Sell(asset, sell_amount))

            if remaining_imbalance <= 0:
                break

        return suggestions
