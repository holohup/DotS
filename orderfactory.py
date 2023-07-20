from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Order:
    spreadid: str
    sell: bool
    amount: int
    price: float


@dataclass(frozen=True)
class TradeLevels:
    levels: list


@dataclass(frozen=True)
class Spread:
    base_asset: str
    expiration: datetime
    buy_levels: TradeLevels
    sell_levels: TradeLevels
    max_amount: int


class OrderFactory:
    def __init__(self, spread: Spread) -> None:
        self._spread = spread
