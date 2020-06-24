import contextlib
from tempfile import NamedTemporaryFile

import pytest
import yaml

from converter.config import Config


@contextlib.contextmanager
def config_file(conf):
    with NamedTemporaryFile("w+") as f:
        yaml.dump(conf, f)
        yield f.name


def test_config_has_mixture_of_cases___values_are_getable_by_lowercase_path():
    config = Config(overrides={"foo": {"BAR": "BAz"}})

    assert config.get("foo.bar") == "BAz"


def test_config_has_a_mixture_sources___normalised_sources_are_merged():
    with config_file({"foo": {"BAR": "BAz", "boo": "Fizz"}}) as p:
        config = Config(
            config_path=p, overrides={"FOO": {"bar": "Bamm", "BiFF": "Baff"}}
        )

        assert config.get("foo.bar") == "Bamm"
        assert config.get("foo.boo") == "Fizz"
        assert config.get("foo.biff") == "Baff"


def test_config_is_missing_property_without_fallback___key_error_is_raised():
    config = Config(overrides={"foo": {"BAR": "BAz"}},)

    with pytest.raises(KeyError):
        config.get("foo.boo")


def test_config_is_missing_property_with_fallback___fallback_is_used():
    config = Config(overrides={"foo": {"BAR": "BAz"}},)

    assert config.get("foo.boo", "fallback value") == "fallback value"
