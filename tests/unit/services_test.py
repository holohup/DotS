# import pytest

# from service_layer import handlers


# def test_error_for_invalid_spread(spread, fake_repo):
#     repo = fake_repo([spread])
#     with pytest.raises(handlers.SpreadNotFound):
#         handlers.get_buy_order(repo, 'AaAaAaA')
#     with pytest.raises(handlers.SpreadNotFound):
#         handlers.get_sell_order(repo, 'AaAaAaA')


# def test_add_spread(fake_repo):
#     repo = fake_repo([])
#     handlers.add_spread(repo, 'aaa', (1, 2, 3), (4, 5, 6), 6)
#     spread = repo.get('aaa')
#     assert spread is not None
#     assert spread.buy_prices == [3, 2, 1]
#     assert spread.sell_prices == [4, 5, 6]
#     assert spread.max_amount == 6
