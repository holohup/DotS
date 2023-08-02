from domain import events


def handle(event: events.Event):
    queue = [event]
    while queue:
        event = events.pop(0)
        for handler in HANDLERS[type(event)]:
            handler(event)
            queue.extend


def print_event(event: events.Event):
    print(f'{event}')


HANDLERS = {
    # events.OrderBookUpdated: [print_event],
    # events.OpenPositionsUpdated: [print_event]
    events.OrderBookUpdated: [print_event]
}
