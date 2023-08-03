from decimal import Decimal
from typing import OrderedDict
from tinkoff.invest.utils import quotation_to_decimal
from config import TCS_RO_TOKEN, TCS_RW_TOKEN, TCS_ACCOUNT_ID
from tinkoff.invest import OrderBookInstrument, RequestError, Client
from grpc import StatusCode
from tinkoff.invest.retrying.sync.client import RetryingClient
from tinkoff.invest.retrying.settings import RetryClientSettings
from tinkoff.invest.services import MarketDataStreamManager
import threading
import time
from tinkoff.invest import (
    OrderDirection,
    OrderType,
    OrderExecutionReportStatus as OERS,
)
from datetime import datetime
from adapters.api.tradingtime import TradingTime


class TCSApi:
    def __init__(self) -> None:
        self._near_ob = None
        self._next_ob = None
        self._orderbooks = OrderedDict()
        self.market_data_stream: MarketDataStreamManager = None
        self._trading_time = TradingTime()

    def subscribe(self, ob1, ob2, cfgs):
        self._near_ob = ob1
        self._next_ob = ob2
        self._orderbooks[cfgs[0].figi] = ob1
        self._orderbooks[cfgs[1].figi] = ob2
        thread = threading.Thread(
            target=self._subscribe_to_prices, daemon=True, name="tcs"
        )
        thread.start()

    def _subscribe_to_prices(self):
        with RetryingClient(TCS_RO_TOKEN, RetryClientSettings()) as client:
            while True:
                self._create_stream_and_subscribe(client)
                try:
                    self.receive_orderbook()
                except RequestError as e:
                    print(f'!!!!!!!!!!!!!! {e.code=}')
                    if (
                        e.code == StatusCode.UNAVAILABLE
                        or e.code == StatusCode.UNKNOWN
                    ):
                        print('stream unavailable, waiting 60 seconds')
                        retry_time = 60
                    elif e.code == StatusCode.CANCELLED:
                        retry_time = e.metadata.ratelimit_reset
                    self._set_orderbooks_to_none()
                    self._stop_stream()
                    time.sleep(retry_time)
                    print('trying to reconnect to stream...')

    def _set_orderbooks_to_none(self):
        for ob in self._orderbooks.values():
            ob.update_bid(None)
            ob.update_ask(None)

    def receive_orderbook(self):
        for marketdata in self.market_data_stream:
            if not self._trading_time.is_trading_now:
                self._wait_till_trading_starts()
                break
            ob = marketdata.orderbook
            if not ob or not ob.bids or not ob.asks:
                self._set_orderbooks_to_none()
                continue
            bid = float(
                quotation_to_decimal(marketdata.orderbook.bids[0].price)
            )
            ask = float(
                quotation_to_decimal(marketdata.orderbook.asks[0].price)
            )
            self._orderbooks[ob.figi].update_ask(ask)
            self._orderbooks[ob.figi].update_bid(bid)

    def _stop_stream(self):
        if self.market_data_stream:
            print('stopping stream')
            self.market_data_stream.stop()

    def _create_stream_and_subscribe(self, client):
        print('creating a new tcs stream connection')
        self.market_data_stream = client.create_market_data_stream()
        self.market_data_stream.order_book.subscribe(
            instruments=[
                OrderBookInstrument(figi=figi, depth=1)
                for figi in self._orderbooks.keys()
            ]
        )

    def _get_figi(self, next: bool) -> str:
        if next is True:
            return list(self._orderbooks.keys())[1]
        return list(self._orderbooks.keys())[0]

    def _post_market_order(self, figi, direction, amount):
        with Client(TCS_RW_TOKEN) as client:
            r = None
            r = client.orders.post_order(
                figi=figi,
                quantity=amount,
                direction=direction,
                account_id=TCS_ACCOUNT_ID,
                order_type=OrderType.ORDER_TYPE_MARKET,
                order_id=str(datetime.utcnow().timestamp()),
            )
        id = r.order_id
        if (
            r
            and r.execution_report_status
            == OERS.EXECUTION_REPORT_STATUS_FILL
        ):
            with Client(token=TCS_RO_TOKEN) as client:
                r = client.orders.get_order_state(
                    account_id=TCS_ACCOUNT_ID, order_id=id
                )
                i_info = client.instruments.get_futures_margin(
                    figi=figi
                )
            min_price_increment = quotation_to_decimal(
                i_info.min_price_increment
            )
            min_price_increment_amount = quotation_to_decimal(
                i_info.min_price_increment_amount
            )
            usd_to_rub_rate = (
                min_price_increment_amount / min_price_increment
            ) / Decimal('100')
            comission = quotation_to_decimal(r.executed_commission)
            comission_in_usd = float(comission / usd_to_rub_rate)
            average_position_price = quotation_to_decimal(
                r.average_position_price
            )

            price_in_pt = float(
                average_position_price
                / (min_price_increment_amount / min_price_increment)
            )
            message = (
                f'TCS order filled: {amount} for {price_in_pt}, comission:'
                f' {comission_in_usd}, direction: {direction}'
            )
            print(message)

    def buy(self, amount, next):
        figi = self._get_figi(next)
        self._post_market_order(
            figi, OrderDirection.ORDER_DIRECTION_BUY, amount
        )

    def sell(self, amount, next):
        figi = self._get_figi(next)
        self._post_market_order(
            figi, OrderDirection.ORDER_DIRECTION_SELL, amount
        )

    def get_open_positions(self):
        near_pos = next_pos = 0
        with RetryingClient(TCS_RO_TOKEN, RetryClientSettings()) as client:
            r = client.operations.get_positions(account_id=TCS_ACCOUNT_ID)
        for pos in r.futures:
            if list(self._orderbooks.keys())[0] == pos.figi:
                near_pos = pos.balance
            if list(self._orderbooks.keys())[1] == pos.figi:
                next_pos = pos.balance
        return near_pos, next_pos

    def _wait_till_trading_starts(self):
        sleep_time = self._trading_time.seconds_till_trading_starts
        self._set_orderbooks_to_none()
        self._stop_stream()
        print(f'Not a trading time, waiting {sleep_time // 60} minutes')
        time.sleep(sleep_time)
        print('Resuming trading')
