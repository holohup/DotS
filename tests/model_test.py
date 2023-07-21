from model import Spread, Order
import pytest
from exceptions import NoMoreOrders


def all_order_fields_except_id_match(
    order: Order, order_id: str, sell: bool, amount: int, price: float
):
    return all(
        (
            isinstance(order, Order),
            order.spread_id == order_id,
            order.sell == sell,
            order.amount == amount,
            order.price == price,
        )
    )


def test_correct_orders_after_init_without_open_positions(
    spread: Spread,
):
    for (
        expected_buy_price,
        expected_buy_amount,
        expected_sell_price,
        expected_sell_amount,
    ) in ((0.0, 3, 4.5, 3), (-0.5, 2, 5.0, 2), (-1.0, 1, 5.5, 1)):
        assert all_order_fields_except_id_match(
            spread.generate_sell_order(),
            spread.spread_id,
            True,
            expected_sell_amount,
            expected_sell_price,
        )
        assert all_order_fields_except_id_match(
            spread.generate_buy_order(),
            spread.spread_id,
            False,
            expected_buy_amount,
            expected_buy_price,
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
    assert all_order_fields_except_id_match(
        spread.generate_buy_order(),
        spread_creds[0],
        False,
        buy_amount,
        buy_price,
    )
    assert all_order_fields_except_id_match(
        spread.generate_sell_order(),
        spread_creds[0],
        True,
        sell_amount,
        sell_price,
    )


def test_correct_orders_generated_on_init_with_all_spreads(spread_creds):
    spread = Spread(*spread_creds, open_positions=6)
    assert spread.generate_sell_order().amount == 6
    with pytest.raises(NoMoreOrders):
        spread.generate_buy_order()
    spread = Spread(*spread_creds, open_positions=-6)
    assert spread.generate_buy_order().amount == 6
    with pytest.raises(NoMoreOrders):
        spread.generate_sell_order()
