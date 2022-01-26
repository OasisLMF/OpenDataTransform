from hypothesis import given
from hypothesis.strategies import sampled_from

from converter.config import Config


@given(sampled_from(["a", "a.b", "a.b.c"]))
def test_set___internal_dict_is_updated(config_path):
    config = Config()

    config.set(config_path, "foo")

    assert config.get(config_path) == "foo"
