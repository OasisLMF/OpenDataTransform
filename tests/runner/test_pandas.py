import os
from tempfile import TemporaryDirectory

from converter.config import Config
from converter.files.yaml import write_yaml
from converter.mapping import FileMapping
from converter.runner import PandasRunner
from converter.runner.base import NotSet
from tests.runner.test_base import FakeConnector


def test_when_is_false___other_transforms_are_performed_warning_is_written():
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
                    "c": [{"transformation": "a * 2", "when": "False"}],
                    "d": [{"transformation": "b + 3"}],
                },
            },
        )

        # run forward
        forward_mapping = FileMapping(
            Config(),
            input_format="A",
            output_format="B",
            standard_search_path=search,
            search_working_dir=False,
        )
        forward_extractor = FakeConnector(data=input_data)
        forward_loader = FakeConnector()

        PandasRunner(Config()).run(
            forward_extractor, forward_mapping, forward_loader
        )

        assert list(forward_loader.data) == [
            {"c": NotSet, "d": 5},
            {"c": NotSet, "d": 7},
            {"c": NotSet, "d": 9},
            {"c": NotSet, "d": 11},
        ]


def test_runner_handles_when_secondary_cases_are_false():
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
                        {"transformation": "a * 3", "when": "False"},
                    ],
                    "d": [{"transformation": "b + 3"}],
                },
            },
        )

        # run forward
        forward_mapping = FileMapping(
            Config(),
            input_format="A",
            output_format="B",
            standard_search_path=search,
            search_working_dir=False,
        )
        forward_extractor = FakeConnector(data=input_data)
        forward_loader = FakeConnector()

        PandasRunner(Config()).run(
            forward_extractor, forward_mapping, forward_loader
        )

        assert list(forward_loader.data) == [
            {"c": 2, "d": 5},
            {"c": 6, "d": 7},
            {"c": 10, "d": 9},
            {"c": 14, "d": 11},
        ]
