class OrderBook:
    id_counter = 100

    def __init__(self, bid=None, ask=None) -> None:
        self.bid = bid
        self.ask = ask
        self.id = OrderBook.id_counter
        OrderBook.id_counter += 1
        self._deltas = []

    def update_bid(self, bid=None):
        if bid != self.bid:
            self.bid = bid
            self._update_deltas()

    def update_ask(self, ask=None):
        if ask != self.ask:
            self.ask = ask
            self._update_deltas()

    def register_delta(self, delta):
        self._deltas.append(delta)

    def _update_deltas(self):
        for delta in self._deltas:
            delta.update()

    def __repr__(self) -> str:
        return f'Orderbook id {self.id}: {self.bid} - {self.ask}'


class OrderBookDelta:
    def __init__(self, maker_book: OrderBook, taker_book: OrderBook) -> None:
        self.m_book = maker_book
        self.t_book = taker_book
        self._trader = None

    @property
    def sell_delta(self) -> float:
        if self.t_book.bid and self.m_book.ask:
            return round((self.t_book.bid - self.m_book.ask), 10)
        return None

    @property
    def buy_delta(self) -> float:
        if self.t_book.ask and self.m_book.bid:
            return round((self.t_book.ask - self.m_book.bid), 10)
        return None

    def register_trader(self, trader):
        self._trader = trader

    def update(self) -> None:
        if self._trader is not None:
            self._trader.trade_cycle()

    def __repr__(self) -> str:
        return f'{self.m_book=}, {self.t_book=}'
