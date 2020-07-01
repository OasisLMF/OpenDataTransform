import os
from tempfile import TemporaryDirectory

import pytest
from hypothesis import given, settings
from hypothesis.strategies import sampled_from

from converter.connector import BaseConnector
from converter.files import write_yaml
from converter.mapping import BaseMapping, FileMapping
from converter.runner import BaseRunner, ModinRunner, PandasRunner


def runners():
    return sampled_from([PandasRunner, ModinRunner])


class FakeConnector(BaseConnector):
    def __init__(self, data=None, **options):
        super().__init__(**options)
        self.data = data

    def extract(self):
        return self.data

    def load(self, data):
        self.data = list(data)


@given(runner_class=runners())
@settings(deadline=None)
def test_mapping_applies_to_all_cols___forward_and_reverse_gets_to_the_input(
    runner_class,
):
    input_data = [
        {"a": 1, "b": 2},
        {"a": 3, "b": 4},
        {"a": 5, "b": 6},
        {"a": 7, "b": 8},
    ]

    with TemporaryDirectory() as search:
        write_yaml(
            os.path.join(search, "A-B.yml"),
            {
                "input_format": "A",
                "output_format": "B",
                "forward_transform": {
                    "c": [{"transformation": "a * 2"}],
                    "d": [{"transformation": "b + 3"}],
                },
                "reverse_transform": {
                    "a": [{"transformation": "c / 2"}],
                    "b": [{"transformation": "d - 3"}],
                },
            },
        )

        # run forward
        forward_mapping = FileMapping(
            input_format="A", output_format="B", standard_search_path=search,
        )
        forward_extractor = FakeConnector(data=input_data)
        forward_loader = FakeConnector()

        runner_class().run(forward_extractor, forward_mapping, forward_loader)

        assert list(forward_loader.data) == [
            {"c": 2, "d": 5},
            {"c": 6, "d": 7},
            {"c": 10, "d": 9},
            {"c": 14, "d": 11},
        ]

        # reverse runner
        reverse_mapping = FileMapping(
            input_format="B", output_format="A", standard_search_path=search,
        )
        reverse_extractor = forward_loader
        reverse_loader = FakeConnector()

        runner_class().run(reverse_extractor, reverse_mapping, reverse_loader)

        assert list(reverse_loader.data) == input_data


@given(runner_class=runners())
@settings(deadline=None)
def test_multiple_mapping_steps___forward_and_reverse_gets_to_the_input(
    runner_class,
):
    input_data = [
        {"a": 1, "b": 2},
        {"a": 3, "b": 4},
        {"a": 5, "b": 6},
        {"a": 7, "b": 8},
    ]

    with TemporaryDirectory() as search:
        write_yaml(
            os.path.join(search, "A-B.yml"),
            {
                "input_format": "A",
                "output_format": "B",
                "forward_transform": {
                    "c": [{"transformation": "a * 2"}],
                    "d": [{"transformation": "b + 3"}],
                },
                "reverse_transform": {
                    "a": [{"transformation": "c / 2"}],
                    "b": [{"transformation": "d - 3"}],
                },
            },
        )
        write_yaml(
            os.path.join(search, "B-C.yml"),
            {
                "input_format": "B",
                "output_format": "C",
                "forward_transform": {
                    "e": [{"transformation": "c * 3"}],
                    "f": [{"transformation": "d + 4"}],
                },
                "reverse_transform": {
                    "c": [{"transformation": "e / 3"}],
                    "d": [{"transformation": "f - 4"}],
                },
            },
        )

        # run forward
        forward_mapping = FileMapping(
            input_format="A", output_format="C", standard_search_path=search,
        )
        forward_extractor = FakeConnector(data=input_data)
        forward_loader = FakeConnector()

        runner_class().run(forward_extractor, forward_mapping, forward_loader)

        assert list(forward_loader.data) == [
            {"e": 6, "f": 9},
            {"e": 18, "f": 11},
            {"e": 30, "f": 13},
            {"e": 42, "f": 15},
        ]

        # reverse runner
        reverse_mapping = FileMapping(
            input_format="C", output_format="A", standard_search_path=search,
        )
        reverse_extractor = forward_loader
        reverse_loader = FakeConnector()

        runner_class().run(reverse_extractor, reverse_mapping, reverse_loader)

        assert list(reverse_loader.data) == input_data


@given(runner_class=runners())
@settings(deadline=None)
def test_multiple_transforms_could_apply___first_is_applied(runner_class,):
    input_data = [
        {"a": 1, "b": 2},
        {"a": 3, "b": 4},
        {"a": 5, "b": 6},
        {"a": 7, "b": 8},
    ]

    with TemporaryDirectory() as search:
        write_yaml(
            os.path.join(search, "A-B.yml"),
            {
                "input_format": "A",
                "output_format": "B",
                "forward_transform": {
                    "c": [
                        {"transformation": "a * 2"},
                        {"transformation": "a * 4"},
                    ],
                    "d": [{"transformation": "b + 3"}],
                },
                "reverse_transform": {
                    "a": [{"transformation": "c / 2"}],
                    "b": [{"transformation": "d - 3"}],
                },
            },
        )

        # run forward
        forward_mapping = FileMapping(
            input_format="A", output_format="B", standard_search_path=search,
        )
        forward_extractor = FakeConnector(data=input_data)
        forward_loader = FakeConnector()

        runner_class().run(forward_extractor, forward_mapping, forward_loader)

        assert list(forward_loader.data) == [
            {"c": 2, "d": 5},
            {"c": 6, "d": 7},
            {"c": 10, "d": 9},
            {"c": 14, "d": 11},
        ]

        # reverse runner
        reverse_mapping = FileMapping(
            input_format="B", output_format="A", standard_search_path=search,
        )
        reverse_extractor = forward_loader
        reverse_loader = FakeConnector()

        runner_class().run(reverse_extractor, reverse_mapping, reverse_loader)

        assert list(reverse_loader.data) == input_data


@given(runner_class=runners())
@settings(deadline=None)
def test_row_is_value___value_is_set_on_all_columns(runner_class,):
    input_data = [
        {"a": 1, "b": 2},
        {"a": 3, "b": 4},
        {"a": 5, "b": 6},
        {"a": 7, "b": 8},
    ]

    with TemporaryDirectory() as search:
        write_yaml(
            os.path.join(search, "A-B.yml"),
            {
                "input_format": "A",
                "output_format": "B",
                "forward_transform": {
                    "c": [{"transformation": "a * 2"}],
                    "d": [{"transformation": "b + 3"}],
                    "e": [{"transformation": "'foo'"}],
                },
                "reverse_transform": {
                    "a": [{"transformation": "c / 2"}],
                    "b": [{"transformation": "d - 3"}],
                },
            },
        )

        # run forward
        forward_mapping = FileMapping(
            input_format="A", output_format="B", standard_search_path=search,
        )
        forward_extractor = FakeConnector(data=input_data)
        forward_loader = FakeConnector()

        runner_class().run(forward_extractor, forward_mapping, forward_loader)

        assert list(forward_loader.data) == [
            {"c": 2, "d": 5, "e": "foo"},
            {"c": 6, "d": 7, "e": "foo"},
            {"c": 10, "d": 9, "e": "foo"},
            {"c": 14, "d": 11, "e": "foo"},
        ]

        # reverse runner
        reverse_mapping = FileMapping(
            input_format="B", output_format="A", standard_search_path=search,
        )
        reverse_extractor = forward_loader
        reverse_loader = FakeConnector()

        runner_class().run(reverse_extractor, reverse_mapping, reverse_loader)

        assert list(reverse_loader.data) == input_data


def test_base_transform_raises():
    with pytest.raises(NotImplementedError):
        BaseRunner().transform(
            BaseConnector(), BaseMapping(input_format="A", output_format="B"),
        )
