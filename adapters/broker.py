from abc import ABC, abstractmethod
from dataclasses import dataclass
from adapters.api import ib


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
    pass
    # def __init__(self) -> None:
    #     self._config = config
    #     self.setup()

    # @abstractmethod
    # def setup(self):
    #     pass

    # @abstractmethod
    # def subscribe_to_prices(ob):
    #     pass


class TCSBroker(Broker):

    def subscribe_to_prices(self, ob):
        pass


class IBBroker(Broker):
    def __init__(self) -> None:
        self._api = ib.IBApi()
        # self._watcher = ib.IBWatcher()

    def subscribe_to_prices(self, ob):
        pass


