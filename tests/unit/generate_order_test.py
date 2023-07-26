import pytest

from domain.model import (NoMoreOrders, Order, Spread, generate_buy_order,
                          generate_sell_order)


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
