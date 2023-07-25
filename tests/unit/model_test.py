import pytest
from exceptions import MaxAmountTooSmall
from domain.model import Spread


@pytest.mark.parametrize('max_amount', (-5, -1, 0, 1, 2))
def test_exception_raises_with_max_amount_too_small(max_amount):
    with pytest.raises(MaxAmountTooSmall):
        Spread('b', [2.0, 0.0, 1.0], [5, 4, 6], max_amount)
