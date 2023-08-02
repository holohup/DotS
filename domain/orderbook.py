class OrderBook:
    id_counter = 100

    def __init__(self, bid=None, ask=None) -> None:
        self.bid = bid
        self.ask = ask
        self.id = OrderBook.id_counter
        OrderBook.id_counter += 1

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

    @property
    def sell_delta(self) -> float:
        return round((self.t_book.bid - self.m_book.ask), 10)

    @property
    def buy_delta(self) -> float:
        return round((self.t_book.ask - self.m_book.bid), 10)
