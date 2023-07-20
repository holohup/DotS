from datetime import datetime


def id_factory(base_asset: str, expiration: datetime):
    return f'{base_asset}-{expiration.strftime("%B-%y").lower()}'
