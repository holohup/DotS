from datetime import datetime
from model import Spread, Order
from tools import id_factory
import pytest
from exceptions import NoMoreOrders


@pytest.fixture
def spread_creds():
    buy_levels = set((0.0, -0.5, -1.0))
    sell_levels = set((4.5, 5.0, 5.5))
    base_asset = 'gd'
    expiration = datetime(2024, 7, 28)
    spread_id = id_factory(base_asset, expiration)
    max_amount = 6
    return spread_id, buy_levels, sell_levels, max_amount

@pytest.fixture
def spread(spread_creds):
    return Spread(*spread_creds)


def test_correct_orders_after_init_without_open_positions(
    spread: Spread,
):
    for (
        expected_buy_price,
        expected_buy_amount,
        expected_sell_price,
        expected_sell_amount,
    ) in ((0.0, 3, 4.5, 3), (-0.5, 2, 5.0, 2), (-1.0, 1, 5.5, 1)):
        assert spread.generate_sell_order() == Order(
            spread._spread_id, True, expected_sell_amount, expected_sell_price
        )
        assert spread.generate_buy_order() == Order(
            spread._spread_id, False, expected_buy_amount, expected_buy_price
        )


def test_no_more_orders_exception_raises(spread: Spread):
    for _ in range(3):
        spread.generate_buy_order()
        spread.generate_sell_order()
    with pytest.raises(NoMoreOrders):
        spread.generate_buy_order()
    with pytest.raises(NoMoreOrders):
        spread.generate_sell_order()


@pytest.mark.parametrize(
    ('pos', 'expected_buy_amount', 'expected_sell_amount'),
    ((-3, 4, 2), (3, 2, 4), (0, 2, 2)),
)
def test_update_open_positions_negative_works(
    spread: Spread, pos, expected_buy_amount, expected_sell_amount
):
    spread.generate_buy_order()
    spread.generate_sell_order()
    spread.update_open_positions(pos)
    assert spread.generate_buy_order().amount == expected_buy_amount
    assert spread.generate_sell_order().amount == expected_sell_amount


def test_correct_next_orders_if_initialized_with_open_positions(spread_creds):
    spread_id, buy_levels, sell_levels, max_amount = spread_creds
    spread = Spread(*spread_creds, open_positions=-3)
    assert spread.generate_buy_order() == Order(spread_id, False, 4, 0.0)
    assert spread.generate_sell_order() == Order(spread_id, True, 2, 5.0)
