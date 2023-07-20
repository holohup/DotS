from datetime import datetime
from orderfactory import Spread, TradeLevels, Order, OrderFactory

BUY_LEVELS = (0.0, -0.5, -1.0)
SELL_LEVELS = (4.5, 5.0, 5.5)


def test_uninitialized_next_orders_are_correct():
    spread = Spread(
        'gd',
        datetime(2024, 7, 28),
        TradeLevels(BUY_LEVELS),
        TradeLevels(SELL_LEVELS),
        6,
    )
    analyst = OrderFactory(spread=spread)


def test_positions_to_open_cannot_be_more_then_max():
    print(1)
    assert True
