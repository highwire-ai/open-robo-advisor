from .holdings import Holdings
from .transaction import Transaction, Deposit, Withdraw, Buy, Sell

from datetime import date
from decimal import Decimal
from enum import Enum, auto
from typing import List


class AccountType(Enum):
    UNKNOWN = -1
    BROKERAGE = auto()
    TYPE_401A = auto()
    TYPE_401K = auto()
    TYPE_403B = auto()
    TYPE_457B = auto()
    TYPE_529 = auto()
    IRA = auto()
    ROTH_IRA = auto()
    ROTH_401k = auto()
    UGMA = auto()
    UTMA = auto()


class Account:
    def __init__(
        self,
        name: str,
        transactions: List[Transaction],
        account_type: AccountType = AccountType.BROKERAGE,
    ) -> None:
        self.account_type = account_type
        self.transactions = transactions

    def holdings(self, as_of: date | None = None) -> Holdings:
        transaction_date_as_of = as_of or date.today()
        current_cash = Decimal(0)
        settled_cash = Decimal(0)
        current_holdings: dict[str, Decimal] = {}
        settled_holdings: dict[str, Decimal] = {}

        for transaction in self.transactions:
            if transaction.transaction_date <= transaction_date_as_of:
                if type(transaction) is Deposit:
                    current_cash += transaction.amount
                    if transaction.settlement_date and transaction.settlement_date <= transaction_date_as_of:
                        settled_cash += transaction.amount
                elif type(transaction) is Withdraw:
                    current_cash -= transaction.amount
                    if transaction.settlement_date and transaction.settlement_date <= transaction_date_as_of:
                        settled_cash -= transaction.amount
                elif type(transaction) is Buy and transaction.symbol:
                    current_cash -= transaction.amount
                    current_holdings[transaction.symbol] = current_holdings.get(transaction.symbol, Decimal(0)) + (transaction.quantity or Decimal(0))
                    if transaction.settlement_date and transaction.settlement_date <= transaction_date_as_of:
                        settled_cash -= transaction.amount
                        settled_holdings[transaction.symbol] = settled_holdings.get(transaction.symbol, 0) + transaction.quantity
                elif type(transaction) is Sell and transaction.symbol:
                    current_cash += transaction.amount - transaction.fees
                    current_holdings[transaction.symbol] = current_holdings.get(transaction.symbol, Decimal(0)) - (transaction.quantity or Decimal(0))
                    if transaction.settlement_date and transaction.settlement_date <= transaction_date_as_of:
                        settled_cash += transaction.amount - transaction.fees
                        settled_holdings[transaction.symbol] = settled_holdings.get(transaction.symbol, 0) - transaction.quantity

        return Holdings(transaction_date_as_of, current_cash, settled_cash, current_holdings, settled_holdings)
