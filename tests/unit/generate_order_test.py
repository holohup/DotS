import pytest

from domain.model import (NoMoreOrders, Spread, generate_buy_order,
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


def test_correct_errors_on_max_init_without_positions(spread_creds):
    spread = Spread(*spread_creds, open_positions=6)
    with pytest.raises(NoMoreOrders):
        generate_buy_order(spread)
    spread = Spread(*spread_creds, open_positions=-6)
    with pytest.raises(NoMoreOrders):
        generate_sell_order(spread)
