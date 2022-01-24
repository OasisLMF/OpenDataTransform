from hypothesis import given
from hypothesis.strategies import sampled_from

from converter.config import Config
from converter.config.config import deep_merge_dictionary_items


def config_builder(d):
    return Config(overrides=d)


@given(
    cls_a=sampled_from([config_builder, dict]),
    cls_b=sampled_from([config_builder, dict]),
)
def test_configs_and_dicts_are_merged_correctly(cls_a, cls_b):
    assert deep_merge_dictionary_items(
        cls_a({"a": "foo", "b": {"b1": "bar", "b2": "boo"}, "c": "caz"}),
        cls_a({"b": {"b2": "bin", "b3": "ban"}, "c": "coo"}),
    ) == {
        "a": "foo",
        "b": {"b1": "bar", "b2": "bin", "b3": "ban"},
        "c": "coo",
    }
