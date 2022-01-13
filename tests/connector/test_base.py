import pytest

from converter.config import Config
from converter.connector import BaseConnector
from tests.config.fakes import fake_config, fake_transformation_config


def test_extract_is_not_implemented():
    with pytest.raises(NotImplementedError):
        BaseConnector(fake_transformation_config()).extract()


def test_load_is_not_implemented():
    with pytest.raises(NotImplementedError):
        BaseConnector(fake_transformation_config()).load([])


@pytest.mark.asyncio
async def test_aextract_is_not_implemented():
    with pytest.raises(NotImplementedError):
        [row async for row in BaseConnector(fake_transformation_config()).aextract()]


@pytest.mark.asyncio
async def test_aload_is_not_implemented():
    async def async_iter(data):
        async for row in data:
            yield row

    with pytest.raises(NotImplementedError):
        await BaseConnector(fake_transformation_config()).aload(async_iter([]))
