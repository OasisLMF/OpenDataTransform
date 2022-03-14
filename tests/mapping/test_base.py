import pytest

from converter.mapping import BaseMapping
from converter.mapping.base import MappingFormat
from tests.config.fakes import fake_transformation_config


def test_get_transformations_raises_a_not_implemented_error():
    with pytest.raises(NotImplementedError):
        mapping = BaseMapping(
            fake_transformation_config(),
            "ACC",
            input_format=MappingFormat(name="A", version="1"),
            output_format=MappingFormat(name="B", version="1"),
        )
        mapping.get_transformations()
