from domain import events


def handle(events: list[events.Event]):
    while events:
        event = events.pop(0)
        for handler in HANDLERS[type(event)]:
            handler(event)


def print_event(event: events.Event):
    print(f'{event}')


HANDLERS = {
    events.OrderBookUpdated: [print_event],
    events.OpenPositionsUpdated: [print_event]
}
