from datetime import datetime

import pytest
from dateutil.relativedelta import relativedelta

from config import CONTRACTS_IN_MAKE, MIN_MARGIN
from domain import tools


def test_correct_spread_id_is_generated():
    assert (
        tools.generate_spread_id('gold', datetime(2010, 12, 1, 0, 0, 0))
        == 'gold-december-10'
    )


@pytest.mark.parametrize(
    ("days_till_expiration", "return_rate", "expected"),
    (
        (0, 0, 0),
        (365, 100, MIN_MARGIN / CONTRACTS_IN_MAKE),
        (365, -100, -MIN_MARGIN / CONTRACTS_IN_MAKE),
    ),
)
def test_correct_return_rate_counted(
    days_till_expiration, return_rate, expected
):
    assert (
        tools.convert_percent_to_cents(
            return_rate,
            datetime.now() + relativedelta(days=days_till_expiration),
        )
        == expected
    )
