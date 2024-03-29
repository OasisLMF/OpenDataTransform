import os
from unittest import mock

import pytest

from converter.config import Config
from tests.config.fakes import fake_config


@pytest.fixture(autouse=True)
def my_thing_mock():
    with mock.patch("os.environ.items", return_value=[]) as _fixture:
        yield _fixture


def test_config_has_mixture_of_cases___values_are_getable_by_lowercase_path():
    config = fake_config(overrides={"foo": {"BAR": "BAz"}})

    assert config.get("foo.bar") == "BAz"


def test_config_file_exists___normalised_from_file_are_used():
    config = fake_config({"foo": {"BAR": "BAz", "boo": "Fizz"}})

    assert config.get("foo.bar") == "BAz"
    assert config.get("foo.boo") == "Fizz"


def test_config_has_cli_args___normalised_from_cli_are_used():
    config = fake_config(argv={"foo.BAR": "BAz", "foo.boo": "Fizz"})

    assert config.get("foo.bar") == "BAz"
    assert config.get("foo.boo") == "Fizz"


def test_config_has_env_options___normalised_from_env_are_used():
    config = fake_config(
        env={
            "CONVERTER_FOO_BAR": "BAz",
            "converter_Foo_boo": "Fizz",
            "ingored_boo_far": "ignored",
        }
    )

    assert config.get("foo.bar") == "BAz"
    assert config.get("foo.boo") == "Fizz"


def test_config_has_list_in_env_options___normalised_from_env_are_used():
    config = fake_config(
        env={
            "CONVERTER_FOO_BAR": '["BAz", "Buzz"]',
            "converter_Foo_boo": "Fizz",
            "ingored_boo_far": "ignored",
        }
    )

    assert config.get("foo.bar") == ["BAz", "Buzz"]
    assert config.get("foo.boo") == "Fizz"


def test_config_has_a_mixture_sources___normalised_sources_are_merged():
    config = fake_config(
        {
            "foo": {
                "BAR": "File Bar",
                "boo": "File Boo",
                "far": "File Far",
                "dar": "File Dar",
            }
        },
        env={
            "converter_foo_BAR": "Env Bar",
            "converter_foo_boo": "Env Boo",
            "converter_foo_far": "Env Far",
        },
        argv={"foo.BAR": "Argv Bar", "foo.boo": "Argv Boo"},
        overrides={"FOO": {"bar": "Ovr Bar"}},
    )

    assert config.get("foo.bar") == "Ovr Bar"
    assert config.get("foo.boo") == "Argv Boo"
    assert config.get("foo.far") == "Env Far"
    assert config.get("foo.dar") == "File Dar"


def test_config_is_missing_property_without_fallback___key_error_is_raised():
    config = fake_config(overrides={"foo": {"BAR": "BAz"}})

    with pytest.raises(KeyError):
        config.get("foo.boo")


def test_config_is_missing_property_with_fallback___fallback_is_used():
    config = fake_config(overrides={"foo": {"BAR": "BAz"}})

    assert config.get("foo.boo", "fallback value") == "fallback value"


def test_missing_of_missing_parent_without_fallback___key_error_is_raised():
    config = fake_config(overrides={"foo": {"BAR": "BAz"}})

    with pytest.raises(KeyError):
        config.get("foo.boo.bash")


def test_missing_of_missing_parent_with_fallback___fallback_is_used():
    config = fake_config(overrides={"foo": {"BAR": "BAz"}})

    assert config.get("foo.boo.bash", "fallback value") == "fallback value"


#
# absolute_path
#


def test_config_path_is_not_set___absolute_path_is_based_off_working_dir():
    config = Config(overrides={"foo": {"BAR": "BAz"}})

    assert config.absolute_path("foo.bar") == os.path.abspath("foo.bar")


def test_config_path_is_set___absolute_path_is_based_off_dir_of_config():
    config = fake_config({"foo": {"BAR": "BAz"}})

    assert config.absolute_path("foo.bar") == os.path.abspath(
        os.path.join(os.path.dirname(config.path), "foo.bar")
    )


def test_argument_path_is_none___absolute_path_is_none():
    config = fake_config({"foo": {"BAR": "BAz"}})

    assert config.absolute_path(None) is None
