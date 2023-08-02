from typing import NamedTuple

import config
from adapters.broker import (Broker, ContractParams, IBBroker,
                             IBContractParams, TCSBroker, TCSContractParams)
from domain.orderbook import OrderBook


class BrokerCreds(NamedTuple):
    contract_params: ContractParams
    broker_class: Broker


BROKER_HANDLERS = {
    'TCSBroker': BrokerCreds(TCSContractParams, TCSBroker),
    'IBBroker': BrokerCreds(IBContractParams, IBBroker),
}


near_maker_ob, next_maker_ob = OrderBook(), OrderBook()
make_broker = BROKER_HANDLERS[config.MAKE_BROKER].broker_class(
    near_maker_ob, next_maker_ob
)
near_maker_config = BROKER_HANDLERS[config.MAKE_BROKER].contract_params(
    **config.near_spread['make_specs']
)
next_maker_config = BROKER_HANDLERS[config.MAKE_BROKER].contract_params(
    **config.next_spread['make_specs']
)
make_broker.register_contracts(near_maker_config, next_maker_config)
make_broker.connect()
make_broker.subscribe()
