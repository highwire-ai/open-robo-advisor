from decimal import Decimal
from openroboadvisor.ledger.account import Account, AccountType
from openroboadvisor.ledger.asset import Currency

def test_single_account() -> None:
    account = Account("My Fidelity Brokerage", AccountType.BROKERAGE)

    settled_subaccount = account.subaccount("Settled")
    current_subaccount = account.subaccount("Current")
    fees_subaccount = account.subaccount("Fees")
    dividends_subaccount = account.subaccount("Dividends")

    assert settled_subaccount == account.subaccount("Settled")
    assert current_subaccount == account.subaccount("Current")
    assert fees_subaccount == account.subaccount("Fees")
    assert dividends_subaccount == account.subaccount("Dividends")

    settled_subaccount.inc(10, Currency('USD'))
    assert 10 == settled_subaccount.assets[Currency('USD')]
