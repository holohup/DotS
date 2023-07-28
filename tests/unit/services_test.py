import pytest

from service_layer import handlers


def test_returns_order(spread, fake_repo):
    repo = fake_repo([spread])
    assert handlers.get_sell_order(repo, spread.spread_id).amount == 3
    assert handlers.get_buy_order(repo, spread.spread_id).amount == 3


def test_error_for_invalid_spread(spread, fake_repo):
    repo = fake_repo([spread])
    with pytest.raises(handlers.SpreadNotFound):
        handlers.get_buy_order(repo, 'AaAaAaA')
    with pytest.raises(handlers.SpreadNotFound):
        handlers.get_sell_order(repo, 'AaAaAaA')


def test_add_spread(fake_repo):
    repo = fake_repo([])
    handlers.add_spread(repo, 'aaa', (1, 2, 3), (4, 5, 6), 6)
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
    handlers.add_spread(repo, *spread_creds, open_positions=open_pos)
    buy_order = handlers.get_buy_order(repo, id)
    sell_order = handlers.get_sell_order(repo, id)
    assert buy_order.spread_id == id
    assert buy_order.sell is False
    assert buy_order.price == b_prices
    assert buy_order.amount == b_amount
    assert sell_order.spread_id == id
    assert sell_order.sell is True
    assert sell_order.price == s_prices
    assert sell_order.amount == s_amount


def test_correct_sell_order_on_max_init_without_positions(
    spread_creds, fake_repo
):
    repo = fake_repo([])
    handlers.add_spread(repo, *spread_creds, open_positions=6)
    sell_order = handlers.get_sell_order(repo, spread_creds[0])
    assert sell_order.spread_id == spread_creds[0]
    assert sell_order.sell is True
    assert sell_order.amount == 6
    assert sell_order.price == 4.5


def test_correct_buy_order_on_max_init_without_positions(
    spread_creds, fake_repo
):
    repo = fake_repo([])
    handlers.add_spread(repo, *spread_creds, open_positions=-6)
    sell_order = handlers.get_buy_order(repo, spread_creds[0])
    assert sell_order.spread_id == spread_creds[0]
    assert sell_order.sell is False
    assert sell_order.amount == 6
    assert sell_order.price == 0.0


def test_correct_orders_after_init_without_open_positions(
    spread_creds, fake_repo
):
    repo = fake_repo([])
    handlers.add_spread(repo, *spread_creds)
    buy_order = handlers.get_buy_order(repo, spread_creds[0])
    sell_order = handlers.get_sell_order(repo, spread_creds[0])
    assert buy_order.spread_id == spread_creds[0]
    assert buy_order.sell is False
    assert buy_order.amount == 3
    assert buy_order.price == 0.0
    assert sell_order.spread_id == spread_creds[0]
    assert sell_order.sell is True
    assert sell_order.amount == 3
    assert sell_order.price == 4.5


def test_update_open_positions(spread_creds, fake_repo):
    repo = fake_repo([])
    handlers.add_spread(repo, *spread_creds)
    current_pos = repo.get(spread_creds[0]).open_positions
    handlers.update_open_positions(repo, spread_creds[0], 3)
    assert repo.get(spread_creds[0]).open_positions == current_pos + 3


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
def test_generate_order_is_correct_with_various_max_pos(
    max_pos, amounts, fake_repo
):
    repo = fake_repo([])
    b_spread_creds = ('b', [2.0, 0.0, 1.0], [5, 4, 6], max_pos)
    s_spread_creds = ('s', [2.0, 0.0, 1.0], [5, 4, 6], max_pos)
    handlers.add_spread(repo, *b_spread_creds)
    handlers.add_spread(repo, *s_spread_creds)

    for a in amounts:
        s_order = handlers.get_sell_order(repo, s_spread_creds[0])
        assert s_order.amount == a
        handlers.update_open_positions(
            repo, s_spread_creds[0], -s_order.amount
        )

        b_order = handlers.get_buy_order(repo, b_spread_creds[0])
        assert b_order.amount == a
        handlers.update_open_positions(repo, b_spread_creds[0], b_order.amount)
