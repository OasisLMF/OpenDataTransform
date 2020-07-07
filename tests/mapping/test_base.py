import pytest

from converter.config import Config
from converter.config.errors import ConfigurationError
from converter.mapping import BaseMapping


def test_mapping_without_input_format_raises_an_error():
    with pytest.raises(
        ConfigurationError, match="input_format not set for the mapping."
    ):
        BaseMapping(Config(), output_format="B")


def test_mapping_without_output_format_raises_an_error():
    with pytest.raises(
        ConfigurationError, match="output_format not set for the mapping."
    ):
        BaseMapping(Config(), input_format="A")


def test_get_transformations_raises_a_not_implemented_error():
    with pytest.raises(NotImplementedError):
        mapping = BaseMapping(Config(), input_format="A", output_format="B")
        mapping.get_transformations()
