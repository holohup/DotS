from domain.model import Spread, Order
from domain.tools import generate_buy_order, generate_sell_order
from exceptions import NoMoreOrders
import pytest


def test_no_more_orders_exception_raises_buy(spread: Spread):
    for _ in range(3):
        amount = generate_buy_order(spread).amount
        spread.update_open_positions(amount)
    with pytest.raises(NoMoreOrders):
        generate_buy_order(spread)


def test_no_more_orders_exception_raises_sell(spread: Spread):
    for _ in range(3):
        amount = generate_sell_order(spread).amount
        spread.update_open_positions(-amount)
    with pytest.raises(NoMoreOrders):
        generate_sell_order(spread)


@pytest.mark.parametrize(
    ('open_pos', 'sell_price', 'sell_amount', 'buy_price', 'buy_amount'),
    (
        (-3, 5.0, 2, 0.0, 4),
        (-5, 5.5, 1, 0.0, 5),
        (3, 4.5, 4, -0.5, 2),
        (4, 4.5, 5, -0.5, 1),
        (5, 4.5, 5, -1.0, 1),
    ),
)
def test_correct_next_orders_if_initialized_with_open_positions(
    spread_creds, open_pos, sell_price, sell_amount, buy_price, buy_amount
):
    spread = Spread(*spread_creds, open_positions=open_pos)
    assert generate_buy_order(spread) == Order(
        spread_creds[0], False, buy_amount, buy_price
    )
    assert generate_sell_order(spread) == Order(
        spread_creds[0], True, sell_amount, sell_price
    )


def test_correct_orders_generated_on_max_init_without_positions(spread_creds):
    spread = Spread(*spread_creds, open_positions=6)
    assert generate_sell_order(spread) == Order(spread.spread_id, True, 6, 4.5)
    with pytest.raises(NoMoreOrders):
        generate_buy_order(spread)
    spread = Spread(*spread_creds, open_positions=-6)
    assert generate_buy_order(spread) == Order(spread.spread_id, False, 6, 0)
    with pytest.raises(NoMoreOrders):
        generate_sell_order(spread)


def test_correct_orders_after_init_without_open_positions(spread: Spread):
    assert generate_sell_order(spread) == Order(spread.spread_id, True, 3, 4.5)
    assert generate_buy_order(spread) == Order(spread.spread_id, False, 3, 0.0)


@pytest.mark.parametrize(
    ('max_pos', 'amounts'),
    (
        (9, (4, 3, 2)),
        (11, (5, 3, 3)),
        (100, (50, 33, 17)),
        (999, (499, 333, 167)),
        (3, (1, 1, 1)),
        (4, (2, 1, 1)),
        (6, (3, 2, 1)),
        (10, (5, 3, 2)),
    ),
)
def test_generate_order_is_correct_with_various_max_pos(max_pos, amounts):
    b_spread = Spread('b', [2.0, 0.0, 1.0], [5, 4, 6], max_pos)
    s_spread = Spread('s', [2.0, 0.0, 1.0], [5, 4, 6], max_pos)
    for a in amounts:
        order = generate_buy_order(b_spread)
        assert order.amount == a
        b_spread.update_open_positions(order.amount)
        order = generate_sell_order(s_spread)
        assert order.amount == a
        s_spread.update_open_positions(-order.amount)
