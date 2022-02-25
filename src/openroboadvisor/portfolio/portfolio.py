from .account import Account, EXTERNAL_BANK_ID
from datetime import date
from openroboadvisor.ledger import Ledger
from openroboadvisor.ledger.account import AccountType
from openroboadvisor.ledger.entry import OpenAccount


class Portfolio:
    def __init__(self) -> None:
        self.ledger = Ledger()
        self.accounts: dict[str, Account] = {}

        self.open_account(
            account_id=EXTERNAL_BANK_ID,
            account_type=AccountType.CHECKING,
            create_date=date(1, 1, 1),
        )

    def open_account(
        self,
        account_id: str,
        account_type: AccountType = AccountType.BROKERAGE,
        create_date: date | None = None,
    ) -> Account:
        self.ledger.record(
            OpenAccount(
                account_id=account_id,
                account_type=account_type,
                entry_date=create_date or date.today(),
            ),
        )

        account = Account(account_id, self.ledger)
        self.accounts[account_id] = account
        return account

    def get_account(self, account_id: str) -> Account | None:
        # Filter all __accounts to hide internal accounts.
        return None if account_id.startswith('__') else self.get(account_id)
