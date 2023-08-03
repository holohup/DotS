from typing import NamedTuple

import config
from adapters.broker import (
    Broker,
    ContractParams,
    IBBroker,
    IBContractParams,
    TCSBroker,
    TCSContractParams,
)
from domain.orderbook import OrderBook, OrderBookDelta
from adapters.trader import Trader
from domain.model import Spread
from domain.tools import generate_spread_id, convert_percent_to_cents


class BrokerCreds(NamedTuple):
    contract_params: ContractParams
    broker_class: Broker


BROKER_HANDLERS = {
    'TCSBroker': BrokerCreds(TCSContractParams, TCSBroker),
    'IBBroker': BrokerCreds(IBContractParams, IBBroker),
}


def connect_and_subscribe(ob1, ob2, broker_name, specs):
    broker = BROKER_HANDLERS[broker_name].broker_class(ob1, ob2)
    near_config = BROKER_HANDLERS[broker_name].contract_params(
        **config.near_spread[specs]
    )
    next_config = BROKER_HANDLERS[broker_name].contract_params(
        **config.next_spread[specs]
    )
    broker.register_contracts(near_config, next_config)
    broker.connect()
    broker.subscribe()
    return broker


def generate_spread(conf):
    sell_prices = conf['sell_prices']
    exp = conf['expiration']
    if sell_prices[-1] == '%':
        converted_prices = [
            convert_percent_to_cents(percent, exp)
            for percent in sell_prices[:-1]
        ]
        sell_prices = converted_prices
    else:
        sell_prices = [price / 100 for price in sell_prices]
    return Spread(
        generate_spread_id(conf['symbol'], exp),
        conf['buy_prices'],
        sell_prices,
        conf['max_amount'],
    )


near_maker_ob, next_maker_ob = OrderBook(), OrderBook()
make_broker: Broker = connect_and_subscribe(
    near_maker_ob, next_maker_ob, config.MAKE_BROKER, 'make_specs'
)
near_taker_ob, next_taker_ob = OrderBook(), OrderBook()
take_broker: Broker = connect_and_subscribe(
    near_taker_ob, next_taker_ob, config.TAKE_BROKER, 'take_specs'
)

near_ob_delta = OrderBookDelta(near_maker_ob, near_taker_ob)
next_ob_delta = OrderBookDelta(next_maker_ob, next_taker_ob)
near_maker_ob.register_delta(near_ob_delta)
near_taker_ob.register_delta(near_ob_delta)
next_maker_ob.register_delta(next_ob_delta)
next_taker_ob.register_delta(next_ob_delta)


near_spread = generate_spread(config.near_spread)
next_spread = generate_spread(config.next_spread)
near_pos, next_pos = take_broker.get_positions()
if near_pos != 0:
    near_spread.update_open_positions(near_pos // config.TAKE_TO_MAKE_RATIO)
if next_pos != 0:
    next_spread.update_open_positions(next_pos // config.TAKE_TO_MAKE_RATIO)

near_trader = Trader(
    near_ob_delta, make_broker, take_broker, near_spread, next=False
)
next_trader = Trader(
    next_ob_delta, make_broker, take_broker, next_spread, next=True
)
near_ob_delta.register_trader(near_trader)
next_ob_delta.register_trader(next_trader)
