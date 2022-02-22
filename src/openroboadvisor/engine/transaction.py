from datetime import date
from decimal import Decimal


class Transaction:
    def __init__(
        self,
        amount: Decimal | int,
        transaction_date: date,
        settlement_date: date | None = None,
        symbol: str | None = None,
        quantity: Decimal | int | None = None,
        price: Decimal | int | None = None,
        fees: Decimal | int | None = None,
    ) -> None:
        self.symbol = symbol
        self.quantity = Decimal(quantity or 0)
        self.price = Decimal(price or 0)
        self.amount = Decimal(amount or 0)
        self.transaction_date = transaction_date
        self.fees = Decimal(fees or 0)
        self.settlement_date = settlement_date


class Deposit(Transaction):
    def __init__(
        self,
        amount: Decimal | int,
        transfer_date: date,
        settlement_date: date | None = None
    ) -> None:
        super().__init__(
            amount,
            transfer_date,
            settlement_date=settlement_date
        )


class Withdraw(Transaction):
    def __init__(
        self,
        amount: Decimal | int,
        transfer_date: date,
        settlement_date: date | None = None
    ) -> None:
        super().__init__(
            amount,
            transfer_date,
            settlement_date=settlement_date
        )


class Buy(Transaction):
    def __init__(
        self,
        symbol: str,
        amount: Decimal | int,
        quantity: Decimal | int,
        price: Decimal | int,
        trade_date: date,
        fees: Decimal | int = 0,
        settlement_date: date | None = None
    ) -> None:
        super().__init__(
            amount,
            trade_date,
            settlement_date=settlement_date,
            symbol=symbol,
            quantity=quantity,
            price=price,
            fees=fees
        )


class Sell(Transaction):
    def __init__(
        self,
        symbol: str,
        amount: Decimal | int,
        quantity: Decimal | int,
        price: Decimal | int,
        trade_date: date,
        fees: Decimal | int = 0,
        settlement_date: date | None = None
    ) -> None:
        super().__init__(
            amount,
            trade_date,
            settlement_date=settlement_date,
            symbol=symbol,
            quantity=quantity,
            price=price,
            fees=fees
        )


class CashDividend(Transaction):
    def __init__(
        self,
        symbol: str,
        amount: Decimal | int,
        transfer_date: date,
        settlement_date: date | None = None
    ) -> None:
        super().__init__(
            amount,
            transfer_date,
            settlement_date=settlement_date,
            symbol=symbol
        )


class StockDividend(Transaction):
    def __init__(
        self,
        symbol: str,
        amount: Decimal | int,
        quantity: Decimal | int,
        price: Decimal | int,
        trade_date: date,
        settlement_date: date | None = None
    ) -> None:
        super().__init__(
            amount,
            trade_date,
            settlement_date=settlement_date,
            symbol=symbol,
            quantity=quantity,
            price=price
        )


class CashAdjustment(Transaction):
    pass


class StockAdjustment(Transaction):
    pass
