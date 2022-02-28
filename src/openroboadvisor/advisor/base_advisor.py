from .suggestion import Suggestion
from abc import ABC, abstractmethod
from openroboadvisor.portfolio import Portfolio
from typing import List


class BaseAdvisor(ABC):
    def __init__(
        self,
        portfolio: Portfolio,
    ) -> None:
        self.portfolio = portfolio

    def get_suggestions(self) -> dict[str, List[Suggestion]]:
        suggestions = {}

        for account_id in self.portfolio.accounts.keys():
            suggestions.setdefault(account_id, []).extend(
                self.get_account_suggestions(account_id)
            )

        return suggestions

    @abstractmethod
    def get_account_suggestions(self, account_id: str) -> List[Suggestion]:
        raise NotImplementedError
