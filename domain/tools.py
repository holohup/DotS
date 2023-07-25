from datetime import datetime
import uuid
from domain.model import Spread, Order
from exceptions import NoMoreOrders


def id_factory(base_asset: str, expiration: datetime):
    return f'{base_asset}-{expiration.strftime("%B-%y").lower()}'


def generate_order_id():
    return str(uuid.uuid4())


def generate_sell_order(spread: Spread) -> Order:
    total_amount = spread.max_amount + spread.open_positions
    prices = spread.sell_prices

    if total_amount >= spread.max_amount:
        amount = total_amount // 2
        price = prices[0]
    else:
        if total_amount < 1:
            raise NoMoreOrders('No more orders.')

        amount, price = get_amount_and_price_with_lesser_amount(
            spread.max_amount, total_amount, prices
        )

    return Order(spread.spread_id, True, amount, price, generate_order_id())


def generate_buy_order(spread: Spread) -> Order:
    total_amount = spread.max_amount - spread.open_positions
    prices = spread.buy_prices

    if total_amount >= spread.max_amount:
        amount = total_amount // 2
        price = prices[0]
    else:
        if total_amount < 1:
            raise NoMoreOrders('No more orders.')

        amount, price = get_amount_and_price_with_lesser_amount(
            spread.max_amount, total_amount, prices
        )

    return Order(spread.spread_id, False, amount, price, generate_order_id())


def get_amount_and_price_with_lesser_amount(max_amount, total_amount, prices):
    regular_amounts = [max_amount // 2, max_amount // 3]
    regular_amounts.append(max_amount - sum(regular_amounts))
    undistributed_amount = total_amount
    reversed_amounts = []
    for ra in regular_amounts[::-1]:
        a = min(undistributed_amount, ra)
        reversed_amounts.append(a)
        undistributed_amount -= a
    for amount, price in zip(reversed_amounts[::-1], prices):
        if amount > 0:
            break
    return amount, price
