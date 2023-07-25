from datetime import datetime
import uuid


def id_factory(base_asset: str, expiration: datetime):
    return f'{base_asset}-{expiration.strftime("%B-%y").lower()}'


def generate_order_id():
    return str(uuid.uuid4())
