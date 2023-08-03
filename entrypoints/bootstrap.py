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


near_maker_ob, next_maker_ob = OrderBook(), OrderBook()
connect_and_subscribe(near_maker_ob, next_maker_ob, config.MAKE_BROKER, 'make_specs')
near_taker_ob, next_taker_ob = OrderBook(), OrderBook()
connect_and_subscribe(near_taker_ob, next_taker_ob, config.TAKE_BROKER, 'take_specs')

near_ob_delta = OrderBookDelta(near_maker_ob, near_taker_ob)
next_ob_delta = OrderBookDelta(next_maker_ob, next_taker_ob)
near_maker_ob.register_delta(near_ob_delta)
near_taker_ob.register_delta(near_ob_delta)
next_maker_ob.register_delta(next_ob_delta)
next_taker_ob.register_delta(next_ob_delta)
