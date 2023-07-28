from dataclasses import dataclass


class Event:
    pass


@dataclass
class OrderBookUpdated(Event):
    ask: float
    bid: float


@dataclass
class OpenPositionsUpdated(Event):
    spread_id: str
    open_positions: int
