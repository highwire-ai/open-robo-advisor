from datetime import date
from decimal import Decimal


class Holdings:
    def __init__(
        self,
        as_of: date,
        current_cash: Decimal | int,
        settled_cash: Decimal | int,
        current_holdings: dict[str, Decimal],
        settled_holdings: dict[str, Decimal]
    ) -> None:
        self.as_of = as_of
        self.current_cash = Decimal(current_cash)
        self.settled_cash = Decimal(settled_cash)
        self.current_holdings = current_holdings
        self.settled_holdings = settled_holdings
