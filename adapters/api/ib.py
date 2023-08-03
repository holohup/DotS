import threading
import time

from ibapi.client import EClient
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.wrapper import EWrapper
from ibapi.execution import Execution
from ibapi.common import TickerId


class IBApi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self._near_ob = None
        self._next_ob = None
        self.next_order_id = None

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

    def buy(self, amount, next):
        contract = self._get_contract(next)
        order = self._generate_market_order(amount)
        order.action = 'BUY'
        o_id = self.next_order_id
        self.placeOrder(o_id, contract, order)
        self.next_order_id += 1

    def sell(self, amount, next):
        contract = self._get_contract(next)
        order = self._generate_market_order(amount)
        order.action = 'SELL'
        o_id = self.next_order_id
        self.placeOrder(o_id, contract, order)
        self.next_order_id += 1

    def _get_contract(self, next: bool):
        if next is True:
            return self._next_contract
        return self._near_contract

    def _generate_market_order(self, amount):
        order = Order()
        order.orderType = 'MKT'
        order.totalQuantity = amount
        order.eTradeOnly = False
        order.firmQuoteOnly = False
        order.orderId = self.next_order_id
        return order

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

    def nextValidId(self, orderId: int):
        self.next_order_id = orderId
        print(f'new order id received: {orderId}')

    def execDetails(
        self, reqId: int, contract: Contract, execution: Execution
    ):
        id = execution.orderId
        filled = int(execution.shares)
        message = f'IB executed order {id}: {filled} for {execution.price}'
        print(message)

    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        print(f'TWS error: {reqId=} {errorCode=}, {errorString=}')
        if errorCode in (2103, 2108, 2110, 1100, 504, 502):
            self.self._near_ob.update_ask(None)
            self.self._near_ob.update_bid(None)
            self.self._next_ob.update_ask(None)
            self.self._next_ob.update_bid(None)
