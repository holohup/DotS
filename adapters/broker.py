from abc import ABC, abstractmethod
from dataclasses import dataclass

from adapters.api import ib, tcs


class ContractParams:
    pass


@dataclass(frozen=True)
class TCSContractParams(ContractParams):
    figi: str


@dataclass(frozen=True)
class IBContractParams(ContractParams):
    exchange: str
    symbol: str
    currency: str
    secType: str
    lastTradeDateOrContractMonth: str


class Broker(ABC):
    def __init__(self, near_ob, next_ob) -> None:
        self._near_ob = near_ob
        self._next_ob = next_ob
        self._api = self._get_api()
        self._contracts = []

    def register_contracts(self, cfg1, cfg2):
        self._contracts.extend([cfg1, cfg2])

    def subscribe(self):
        self._api.subscribe(self._near_ob, self._next_ob, self._contracts)

    @abstractmethod
    def _get_api(self):
        pass

    @abstractmethod
    def connect(self):
        pass


class TCSBroker(Broker):
    def _get_api(self):
        return tcs.TCSApi()

    def connect(self):
        pass


class IBBroker(Broker):
    def _get_api(self):
        return ib.IBApi()

    def connect(self):
        self._api.connect('127.0.0.1', 7496, 2)
