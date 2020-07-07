import pytest

from converter.config import Config
from converter.connector import BaseConnector


def test_extract_is_not_implemented():
    with pytest.raises(NotImplementedError):
        BaseConnector(Config()).extract()


def test_load_is_not_implemented():
    with pytest.raises(NotImplementedError):
        BaseConnector(Config()).load([])
