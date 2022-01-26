import pytest

from converter.config import Config


config = Config(
    overrides={
        "template_transformation": {"a": "bar", "b": "baz"},
        "transformations": {"acc": {"a": "foo"}},
    }
)


def test_value_not_in_path_or_tpl___error_raised():
    with pytest.raises(KeyError):
        config.get_template_resolved_value("transformations.acc.c")


def test_value_not_in_path_but_in_tpl___tpl_value_used():
    assert config.get_template_resolved_value("transformations.acc.b") == "baz"


def test_value_in_path_and_tpl___path_value_used():
    assert config.get_template_resolved_value("transformations.acc.a") == "foo"
