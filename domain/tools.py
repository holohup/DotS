import uuid
from datetime import datetime


def generate_spread_id(base_asset: str, expiration: datetime):
    return f'{base_asset}-{expiration.strftime("%B-%y").lower()}'


def generate_order_id():
    return str(uuid.uuid4())
