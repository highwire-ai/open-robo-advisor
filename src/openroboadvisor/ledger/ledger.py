from openroboadvisor.ledger.account import Account
from openroboadvisor.ledger.entry import CloseAccount, Entry, OpenAccount, Transaction
from typing import List, Callable, cast


EntryHandler = Callable[Entry, None]


class Ledger:
    def __init__(self) -> None:
        self.accounts: dict[str, Account] = {}
        self.entries: List[LedgerEntry] = []
        self.entry_handlers: dict[type, EntryHandler] = {
            OpenAccount: self.handle_open_account,
            CloseAccount: self.handle_close_account,
            Transaction: self.handle_transaction,
        }

    def record(self, *entries: Entry) -> None:
        for entry in entries:
            entry_type = type(entry)
            entry_handler = self.entry_handlers.get(entry_type)
            entry.validate(self.accounts)
            self.entries.append(entry)

            if entry_handler:
                entry_handler(entry)
            else:
                raise Exception(
                    "Unable to process entry for unknown "
                    f"entry type (type='{entry_type.__name__}')"
                )

    def get_account(self, account_id: str) -> Account | None:
        return self.accounts.get(account_id)

    def handle_open_account(self, entry: Entry) -> None:
        open_account_entry = cast(OpenAccount, entry)

        self.accounts[open_account_entry.account_id] = Account(
            account_id=open_account_entry.account_id,
            account_type=open_account_entry.account_type,
        )

    def handle_close_account(self, entry: Entry) -> None:
        raise NotImplementedError

    def handle_transaction(self, entry: Entry) -> None:
        transaction = cast(Transaction, entry)

        for leg in transaction.legs:
            account = self.accounts.get(leg.account_id)

            assert account, (
                "Leg references an account that doesn't exist "
                f"(account_id='{leg.account_id}')"
            )

            subaccount = account.subaccount(leg.subaccount_id)
            subaccount.inc(leg.quantity, leg.asset_type)
