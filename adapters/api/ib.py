from ibapi.wrapper import EWrapper
from ibapi.client import EClient
import threading
import time
from abc import ABC, abstractmethod


class IBApi(EWrapper, EClient):
    def __init__(self):
    # self.ob = ob
    # self.cache = cache
    # self.next_order_id = next_order_id
        EClient.__init__(self, self)



class Watcher(ABC):
    @abstractmethod
    def subscribe_to_prices(self):
        pass


class IBWatcher(Watcher):
    def __init__(self, ib, contracts: list) -> None:
        self.ib = ib
        self.contract = contracts
        thread = threading.Thread(
            target=self.run_loop, daemon=True, name="ibkr"
        )
        thread.start()
        self.subscribe_to_prices()

    def run_loop(self):
        self.ib.run()

    def subscribe_to_prices(self):
        time.sleep(1)
        self.ib.reqMarketDataType(1)
        for contract in self.contracts:
            self.ib.reqMktData(1, contract, "", False, 0, [])
