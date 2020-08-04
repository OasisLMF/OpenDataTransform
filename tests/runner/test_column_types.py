from hypothesis import given, settings

from converter.config import Config
from converter.mapping.base import TransformationEntry, ColumnConversion
from tests.connector.fakes import FakeConnector
from tests.mapping.fakes import make_simple_mapping
from tests.runner.stategies import runners


@given(runner_class=runners())
@settings(deadline=None)
def test_column_is_specified_as_int___values_are_changed_bad_are_excluded(
    runner_class
):
    input_data = [
        {"a": "1"},
        {"a": 3.1},
        {"a": None},
        {"a": "NULL"},
        {"a": "foo"},
    ]

    mapping = make_simple_mapping(
        {"b": [TransformationEntry(transformation="a")],},
        types={
            "a": ColumnConversion(type="int", null_values=[None, "NULL"],),
        },
    )

    extractor = FakeConnector(data=input_data)
    loader = FakeConnector()

    runner_class(Config()).run(extractor, mapping, loader)

    assert list(loader.data) == [
        {"b": 1},
        {"b": 3},
        {"b": None},
        {"b": None},
    ]


@given(runner_class=runners())
@settings(deadline=None)
def test_column_is_specified_as_float___values_are_changed_bad_are_excluded(
    runner_class
):
    input_data = [
        {"a": "1"},
        {"a": 3.1},
        {"a": None},
        {"a": "NULL"},
        {"a": "foo"},
    ]

    mapping = make_simple_mapping(
        {"b": [TransformationEntry(transformation="a")],},
        types={
            "a": ColumnConversion(type="float", null_values=[None, "NULL"],),
        },
    )

    extractor = FakeConnector(data=input_data)
    loader = FakeConnector()

    runner_class(Config()).run(extractor, mapping, loader)

    assert list(loader.data) == [
        {"b": 1},
        {"b": 3.1},
        {"b": None},
        {"b": None},
    ]


@given(runner_class=runners())
@settings(deadline=None)
def test_column_is_specified_as_string___values_are_changed_bad_are_excluded(
    runner_class
):
    input_data = [
        {"a": "1"},
        {"a": 3.1},
        {"a": None},
        {"a": "NULL"},
        {"a": "foo"},
    ]

    mapping = make_simple_mapping(
        {"b": [TransformationEntry(transformation="a")],},
        types={
            "a": ColumnConversion(type="string", null_values=[None, "NULL"],),
        },
    )

    extractor = FakeConnector(data=input_data)
    loader = FakeConnector()

    runner_class(Config()).run(extractor, mapping, loader)

    assert list(loader.data) == [
        {"b": "1"},
        {"b": "3.1"},
        {"b": None},
        {"b": None},
        {"b": "foo"},
    ]
