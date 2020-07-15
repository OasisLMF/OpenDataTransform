import pytest

from converter.config import Config
from converter.connector import BaseConnector


def test_extract_is_not_implemented():
    with pytest.raises(NotImplementedError):
        BaseConnector(Config()).extract()


def test_load_is_not_implemented():
    with pytest.raises(NotImplementedError):
        BaseConnector(Config()).load([])


@pytest.mark.asyncio
async def test_aextract_is_not_implemented():
    with pytest.raises(NotImplementedError):
        [row async for row in BaseConnector(Config()).aextract()]


@pytest.mark.asyncio
async def test_aload_is_not_implemented():
    async def async_iter(data):
        async for row in data:
            yield row

    with pytest.raises(NotImplementedError):
        await BaseConnector(Config()).aload(async_iter([]))
