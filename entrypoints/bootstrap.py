import config

from adapters.broker import (
    TCSBroker,
    IBBroker,
    IBContractParams,
    TCSContractParams,
)
from datetime import datetime
from domain.model import Spread
import importlib
from domain.orderbook import OrderBook, OrderBookDelta


CONTRACT_PARAMS_HANDLERS = {
    'TCSBroker': TCSContractParams,
    'IBBroker': IBContractParams,
}


def generate_spread_id(base_asset: str, expiration: datetime):
    return f'{base_asset}-{expiration.strftime("%B-%y").lower()}'


class ConfigParser:
    def __init__(self, configs: list[dict]) -> None:
        self._configs = configs
        self._spreads = None
        self._seen_orderbooks = dict()
        self._subscription_tasks = dict()
        self._orderbooks = dict()
        for conf in self._configs:
            self._parse_config(conf)

    def _parse_config(self, conf):
        spread = self._create_spread(conf)
        make_broker_cls, take_broker_cls = self.extract_broker_class_names(conf)
        take_contract, make_contract = self._extract_contracts(
            conf, make_broker_cls, take_broker_cls
        )
        take_orderbook, make_orderbook = self._assign_orderbooks(
            take_contract, make_contract
        )
        if take_broker_cls not in self._orderbooks:
            self._orderbooks[take_broker_cls] = set()
        if make_broker_cls not in self._orderbooks:
            self._orderbooks[make_broker_cls] = set()
        self._orderbooks[make_broker_cls].add(make_orderbook)
        self._orderbooks[take_broker_cls].add(take_orderbook)
        ob_delta = OrderBookDelta(make_orderbook, take_orderbook)
        self._subscription_tasks[spread.spread_id] = ob_delta
        make_broker = getattr(
            importlib.import_module('adapters.broker'), make_broker_cls
        )()
        take_broker = getattr(
            importlib.import_module('adapters.broker'), take_broker_cls
        )()
        print(self._seen_orderbooks)
        print(self._orderbooks)

    def _assign_orderbooks(self, take_contract, make_contract):
        if make_contract not in self._seen_orderbooks:
            self._seen_orderbooks[make_contract] = OrderBook()
        if take_contract not in self._seen_orderbooks:
            self._seen_orderbooks[take_contract] = OrderBook()
        take_orderbook = self._seen_orderbooks[make_contract]
        make_orderbook = self._seen_orderbooks[take_contract]
        return take_orderbook, make_orderbook

    def _extract_contracts(self, conf, make_broker_cls, take_broker_cls):
        take_contract = CONTRACT_PARAMS_HANDLERS[take_broker_cls](
            **conf['take_specs']
        )
        make_contract = CONTRACT_PARAMS_HANDLERS[make_broker_cls](
            **conf['make_specs']
        )

        return take_contract, make_contract

    def extract_broker_class_names(self, conf):
        make_broker_cls = conf['make_specs'].pop('broker')
        take_broker_cls = conf['take_specs'].pop('broker')
        return make_broker_cls, take_broker_cls

    def _create_spread(self, conf):
        return Spread(
            generate_spread_id(conf['symbol'], conf['expiration']),
            conf['buy_prices'],
            conf['sell_prices'],
            conf['max_amount'],
        )


parser = ConfigParser(config.generate_spread_configs())


# near_spread = {
#     'take_specs': {'broker': 'TCSBroker', 'figi': 'FUTNG0823000'}, -BROKER, OB
#     'make_specs': {
#         'broker': 'IBBroker',
#         'exchange': 'NYMEX',
#         'symbol': 'QG',
#         'currency': 'USD',
#         'secType': 'FUT',
#     }, - BROKER, OB
#     'take_to_make_ratio': 25, -TRADER
# }
