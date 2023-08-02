import uuid
from datetime import datetime, timedelta
from config import MIN_MARGIN, CONTRACTS_IN_MAKE


def generate_order_id():
    return str(uuid.uuid4())


def generate_spread_id(base_asset: str, expiration: datetime):
    return f'{base_asset}-{expiration.strftime("%B-%y").lower()}'


def convert_percent_to_cents(rr, exp_date: datetime):
    d_t_e = (
        exp_date.replace(hour=23, minute=49, second=59) - datetime.now()
    ).days
    return round(
        rr * MIN_MARGIN * d_t_e / (365 * CONTRACTS_IN_MAKE * 100),
        10,
    )
