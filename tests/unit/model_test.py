from domain.model import Spread, Order, generate_order
import pytest
from exceptions import NoMoreOrders, MaxAmountTooSmall


def test_no_more_orders_exception_raises_buy(spread: Spread):
    for _ in range(3):
        amount = generate_order(spread, False).amount
        spread.update_open_positions(amount)
    with pytest.raises(NoMoreOrders):
        generate_order(spread, False)


def test_no_more_orders_exception_raises_sell(spread: Spread):
    for _ in range(3):
        amount = generate_order(spread, True).amount
        spread.update_open_positions(-amount)
    with pytest.raises(NoMoreOrders):
        generate_order(spread, True)


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
    assert generate_order(spread, False) == Order(
        spread_creds[0], False, buy_amount, buy_price
    )
    assert generate_order(spread, True) == Order(
        spread_creds[0], True, sell_amount, sell_price
    )


def test_correct_orders_generated_on_init_without_positions(spread_creds):
    spread = Spread(*spread_creds, open_positions=6)
    assert generate_order(spread, True) == Order(
        spread.spread_id, True, 6, 4.5
    )
    with pytest.raises(NoMoreOrders):
        generate_order(spread, False)
    spread = Spread(*spread_creds, open_positions=-6)
    assert generate_order(spread, False) == Order(
        spread.spread_id, False, 6, 0
    )
    with pytest.raises(NoMoreOrders):
        generate_order(spread, True)


def test_correct_orders_after_init_without_open_positions(spread: Spread):
    assert generate_order(spread, sell=True) == Order(
        spread.spread_id, True, 3, 4.5
    )
    assert generate_order(spread, sell=False) == Order(
        spread.spread_id, False, 3, 0.0
    )


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
        order = generate_order(b_spread, False)
        assert order.amount == a
        b_spread.update_open_positions(order.amount)
        order = generate_order(s_spread, True)
        assert order.amount == a
        s_spread.update_open_positions(-order.amount)


@pytest.mark.parametrize(
    'max_amount', (-5, -1, 0, 1, 2)
)
def test_exception_raises_with_max_amount_too_small(max_amount):
    with pytest.raises(MaxAmountTooSmall):
        Spread('b', [2.0, 0.0, 1.0], [5, 4, 6], max_amount)
