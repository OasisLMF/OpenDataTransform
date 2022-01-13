import pytest

from converter.config import Config
from converter.mapping import BaseMapping
from converter.mapping.base import MappingFormat


def test_get_transformations_raises_a_not_implemented_error():
    with pytest.raises(NotImplementedError):
        mapping = BaseMapping(
            Config(),
            "ACC",
            input_format=MappingFormat(name="A", version="1"),
            output_format=MappingFormat(name="B", version="1"),
        )
        mapping.get_transformations()
