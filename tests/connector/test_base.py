import pytest

from converter.connector import BaseConnector


def test_extract_is_not_implemented():
    with pytest.raises(NotImplementedError):
        BaseConnector().extract()


def test_load_is_not_implemented():
    with pytest.raises(NotImplementedError):
        BaseConnector().load([])
