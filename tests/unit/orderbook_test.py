import pytest

from domain.orderbook import OrderBook, OrderBookDelta


@pytest.mark.parametrize(
    ("maker_ob", "taker_ob", "result"),
    (((4, 5), (3, 4), 0), ((13.5, 14.5), (10.1, 10.2), -3.3)),
)
def test_correct_buy_spread(maker_ob, taker_ob, result):
    ob_m = OrderBook(*maker_ob)
    ob_t = OrderBook(*taker_ob)
    delta = OrderBookDelta(ob_m, ob_t)
    assert delta.buy_delta == result


@pytest.mark.parametrize(
    ("maker_ob", "taker_ob", "result"),
    (((4, 5), (3, 4), -2), ((13.5, 14.5), (10.1, 10.2), -4.4)),
)
def test_correct_sell_spread(maker_ob, taker_ob, result):
    ob_m = OrderBook(*maker_ob)
    ob_t = OrderBook(*taker_ob)
    delta = OrderBookDelta(ob_m, ob_t)
    assert delta.sell_delta == result
