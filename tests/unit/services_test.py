from service_layer import services
import pytest


def test_returns_order(spread, fake_repo):
    repo = fake_repo([spread])
    assert services.get_sell_order(repo, spread.spread_id).amount == 3
    assert services.get_buy_order(repo, spread.spread_id).amount == 3


def test_error_for_invalid_spread(spread, fake_repo):
    repo = fake_repo([spread])
    with pytest.raises(services.SpreadNotFound):
        services.get_buy_order(repo, 'AaAaAaA')
    with pytest.raises(services.SpreadNotFound):
        services.get_sell_order(repo, 'AaAaAaA')


def test_add_spread(fake_repo):
    repo = fake_repo([])
    services.add_spread(repo, 'aaa', (1, 2, 3), (4, 5, 6), 6)
    spread = repo.get('aaa')
    assert spread is not None
    assert spread.buy_prices == [3, 2, 1]
    assert spread.sell_prices == [4, 5, 6]
    assert spread.max_amount == 6


@pytest.mark.parametrize(
    ('open_pos', 's_prices', 's_amount', 'b_prices', 'b_amount'),
    (
        (-3, 5.0, 2, 0.0, 4),
        (-5, 5.5, 1, 0.0, 5),
        (3, 4.5, 4, -0.5, 2),
        (4, 4.5, 5, -0.5, 1),
        (5, 4.5, 5, -1.0, 1),
    ),
)
def test_next_orders_on_init_witions(
    spread_creds, open_pos, s_prices, s_amount, b_prices, b_amount, fake_repo
):
    id = spread_creds[0]
    repo = fake_repo([])
    services.add_spread(repo, *spread_creds, open_positions=open_pos)
    buy_order = services.get_buy_order(repo, id)
    sell_order = services.get_sell_order(repo, id)
    assert buy_order.spread_id == id
    assert buy_order.sell is False
    assert buy_order.price == b_prices
    assert buy_order.amount == b_amount
    assert sell_order.spread_id == id
    assert sell_order.sell is True
    assert sell_order.price == s_prices
    assert sell_order.amount == s_amount
