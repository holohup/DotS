class OrderBook:
    def __init__(self, bid=None, ask=None) -> None:
        self.bid = bid
        self.ask = ask

    def update_bid(self, bid=None):
        if bid is not None:
            self.bid = bid

    def update_ask(self, ask=None):
        if ask is not None:
            self.ask = ask


class OrderBookDelta:
    def __init__(self, maker_book: OrderBook, taker_book: OrderBook) -> None:
        self.m_book = maker_book
        self.t_book = taker_book
        self._spread_ids = []

    @property
    def sell_delta(self) -> float:
        return round((self.t_book.bid - self.m_book.ask), 10)

    @property
    def buy_delta(self) -> float:
        return round((self.t_book.ask - self.m_book.bid), 10)

    def register_spread(self, spread_id):
        if spread_id not in self._spread_ids:
            self._spread_ids.append(spread_id)
