from datetime import datetime

import pytest

from adapters import repository
from domain.model import Spread
from entrypoints.bootstrap import generate_spread_id


@pytest.fixture
def spread_creds():
    buy_levels = (0.0, -0.5, -1.0)
    sell_levels = (4.5, 5.0, 5.5)
    base_asset = 'gd'
    expiration = datetime(2024, 7, 28)
    spread_id = generate_spread_id(base_asset, expiration)
    max_amount = 6
    return spread_id, buy_levels, sell_levels, max_amount


@pytest.fixture
def spread(spread_creds):
    return Spread(*spread_creds)


@pytest.fixture
def fake_repo():
    return repository.InMemoryRepository
