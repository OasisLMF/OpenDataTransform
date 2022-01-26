import pytest
from hypothesis import given
from hypothesis.strategies import sampled_from

from converter.config import Config


@given(sampled_from(["a", "a.b", "a.b.c"]))
def test_value_is_present__value_is_removed(config_path):
    config = Config()

    config.set(config_path, "foo")
    config.delete(config_path)

    with pytest.raises(KeyError):
        config.get(config_path)


@given(sampled_from(["a", "a.b", "a.b.c"]))
def test_value_is_not_present__config_is_unchanged(config_path):
    config = Config(overrides={"bar": "baz"})

    config.delete(config_path)

    assert config.get("bar") == "baz"
    with pytest.raises(KeyError):
        config.get(config_path)
