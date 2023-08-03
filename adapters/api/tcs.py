from tinkoff.invest.utils import quotation_to_decimal
from config import TCS_RO_TOKEN
from tinkoff.invest import OrderBookInstrument, RequestError
from grpc import StatusCode
from tinkoff.invest.retrying.sync.client import RetryingClient
from tinkoff.invest.retrying.settings import RetryClientSettings
from tinkoff.invest.services import MarketDataStreamManager
import threading
import time


class TCSApi:
    def __init__(self) -> None:
        self._near_ob = None
        self._next_ob = None
        self.market_data_stream: MarketDataStreamManager = None

    def subscribe(self, ob1, ob2, cfgs):
        self._near_ob = ob1
        self._next_ob = ob2
        self._cfgs = cfgs
        self._orderbooks = {cfgs[0]: ob1, cfgs[1]: ob2}
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
                    self.order_book.stream_interrupted = True
                    self.order_book.wait_time = retry_time
                    self.order_book.update_ask(-1.0)
                    self.order_book.update_bid(-1.0)
                    self.stop_stream()
                    time.sleep(retry_time)
                    print('trying to reconnect to stream...')

    def receive_orderbook(self):
        old_near_ask = old_near_bid = old_next_ask = old_next_bid = 0
        for marketdata in self.market_data_stream:
            # if not self.trading_time.is_trading_now:
            #     self.wait_till_trading_starts()
            #     break
            ob = marketdata.orderbook
            if not ob or not ob.bids or not ob.asks:
                print('not statement')
                self.order_book.update_ask(None)
                self.order_book.update_bid(None)
                continue
            bid = float(
                quotation_to_decimal(marketdata.orderbook.bids[0].price)
            )
            ask = float(
                quotation_to_decimal(marketdata.orderbook.asks[0].price)
            )
            self._orderbooks[ob.figi].update_ask(ask)
            self._orderbooks[ob.figi].update_bid(bid)
            print(self._orderbooks)

    def stop_stream(self):
        if self.market_data_stream:
            print('stopping stream')
            self.market_data_stream.stop()

    def _create_stream_and_subscribe(self, client):
        print('creating a new tcs stream connection')
        self.market_data_stream = client.create_market_data_stream()
        self.market_data_stream.order_book.subscribe(
            instruments=[
                OrderBookInstrument(figi=figi, depth=1) for figi in self._cfgs
            ]
        )
