import threading
import time

from ibapi.client import EClient
from ibapi.contract import Contract
from ibapi.wrapper import EWrapper


class IBApi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self._near_ob = None
        self._next_ob = None

    def subscribe(self, ob1, ob2, cfgs):
        self._near_ob = ob1
        self._next_ob = ob2
        thread = threading.Thread(
            target=self._run_loop, daemon=True, name="ibkr"
        )
        thread.start()
        self._subscribe_to_prices(cfgs)

    def _run_loop(self):
        self.run()

    def _subscribe_to_prices(self, cfgs):
        time.sleep(1)
        self._near_contract, self._next_contract = Contract(), Contract()
        print(cfgs)
        for f in (
            'exchange',
            'symbol',
            'currency',
            'secType',
            'lastTradeDateOrContractMonth',
        ):
            setattr(self._near_contract, f, getattr(cfgs[0], f))
            setattr(self._next_contract, f, getattr(cfgs[1], f))
        self.reqMarketDataType(1)
        self.reqMktData(
            self._near_ob.id, self._near_contract, "", False, 0, []
        )
        self.reqMktData(
            self._next_ob.id, self._next_contract, "", False, 0, []
        )

    def tickPrice(self, req_id, tickType, price, attrib):
        if req_id == self._near_ob.id:
            ob = self._near_ob
        elif req_id == self._next_ob.id:
            ob = self._next_ob
        else:
            return
        if tickType == 1:
            ob.update_bid(price)
        elif tickType == 2:
            ob.update_ask(price)
