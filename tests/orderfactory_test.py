from datetime import datetime
from orderfactory import Spread, TradeLevels, Order, OrderFactory
from id_factory import id_factory
import pytest


@pytest.fixture
def sample_spread_creds():
    buy_levels = TradeLevels((0.0, -0.5, -1.0))
    sell_levels = TradeLevels((4.5, 5.0, 5.5))
    return buy_levels, sell_levels


@pytest.fixture
def spread_id():
    base_asset = 'gd'
    expiration = datetime(2024, 7, 28)
    return id_factory(base_asset, expiration)


@pytest.fixture
def sample_spread(sample_spread_creds, spread_id):
    return Spread(spread_id, *sample_spread_creds, 6)


def test_next_orders_are_correct_without_position(sample_spread):
    spreads = [sample_spread]
    of = OrderFactory(spreads)
    assert of.next_sell_order(spread_id) == Order('gd-july-24', True, 3, 4.5)
    assert of.next_buy_order(spread_id) == Order('gd-july-24', False, 3, 0.0)


@pytest.mark.parametrize(('max_amount'), ((3, 8, 100)))
def test_next_orders_are_correct_without_position_various_max_amounts(
    sample_spread_creds, max_amount, spread_id
):
    spread = Spread(spread_id, *sample_spread_creds, max_amount)
    of = OrderFactory([spread])
    assert of.next_sell_order(spread_id).amount == max_amount // 2
    assert of.next_buy_order(spread_id).amount == max_amount // 2


# def test_next_orders_are_correct_with_current_position(sample_spread_creds):
#     spread = Spread(*sample_spread_creds, current_position=3)
#     spreads = [spread]
#     of = OrderFactory(spreads)
#     of.next_sell_order()
#     of.next_buy_order()
#     assert of.next_sell_order() == Order('gd-july-24', True, 2, 5.0)
#     assert of.next_buy_order() == Order('gd-july-24', False, 4, 5.0)
