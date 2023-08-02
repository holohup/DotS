# from adapters.repository import AbstractRepository
# from domain.model import Spread, generate_buy_order, generate_sell_order
# from service_layer import messagebus


# class SpreadNotFound(Exception):
#     pass


# def validate_spread_id(repo, spread_id):
#     spreads = repo.list()
#     if spread_id not in [spread.spread_id for spread in spreads]:
#         raise SpreadNotFound(f'Spread with id={spread_id} not found')


# def get_sell_order(repo: AbstractRepository, spread_id: int):
#     validate_spread_id(repo, spread_id)
#     spread = repo.get(spread_id)
#     return generate_sell_order(spread)


# def get_buy_order(repo: AbstractRepository, spread_id: int):
#     validate_spread_id(repo, spread_id)
#     spread = repo.get(spread_id)
#     return generate_buy_order(spread)


# def add_spread(
#     repo, spread_id, buy_prices, sell_prices, max_amount, open_positions=0
# ):
#     repo.add(
#         Spread(
#    spread_id, buy_prices, sell_prices, max_amount, open_positions
# )
#     )


# def update_open_positions(repo, spread_id, amount):
#     spread = repo.get(spread_id)
#     spread.update_open_positions(amount)
#     messagebus.handle(spread.events)
