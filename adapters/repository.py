from abc import ABC, abstractmethod

from domain.model import Spread


class AbstractRepository(ABC):

    @abstractmethod
    def add(self, spread: Spread) -> None:
        raise NotImplementedError()

    @abstractmethod
    def get(self, spread_id: str) -> Spread:
        raise NotImplementedError()


class InMemoryRepository(AbstractRepository):
    def __init__(self, spreads: list[Spread]) -> None:
        self._spreads = set(spreads)

    def add(self, spread: Spread) -> None:
        self._spreads.add(spread)

    def get(self, spread_id: str) -> Spread:
        return next(s for s in self._spreads if s.spread_id == spread_id)

    def list(self) -> list[Spread]:
        return list(self._spreads)
