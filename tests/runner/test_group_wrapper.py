import pytest

from converter.transformers.transform import GroupWrapper


def test_base_check_fn_raises_not_implemented():
    with pytest.raises(NotImplementedError):
        GroupWrapper([]).check_fn([])
