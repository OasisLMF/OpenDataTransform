import os
from tempfile import TemporaryDirectory

import pytest
from hypothesis import given, settings

from converter.connector import BaseConnector
from converter.files.yaml import write_yaml
from converter.mapping import BaseMapping, FileMapping
from converter.runner import BaseRunner
from converter.runner.base import BaseAsyncRunner
from tests.config.fakes import fake_transformation_config
from tests.connector.fakes import FakeConnector
from tests.runner.stategies import runners


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
                "file_type": "ACC",
                "input_format": {"name": "A", "version": "1"},
                "output_format": {"name": "B", "version": "1"},
                "forward": {
                    "transform": {
                        "c": [{"transformation": "a * 2"}],
                        "d": [{"transformation": "b + 3"}],
                    }
                },
                "reverse": {
                    "transform": {
                        "a": [{"transformation": "c / 2"}],
                        "b": [{"transformation": "d - 3"}],
                    }
                },
            },
        )

        # run forward
        forward_mapping = FileMapping(
            fake_transformation_config(),
            "ACC",
            standard_search_path=search,
            search_working_dir=False,
        )
        forward_extractor = FakeConnector(data=input_data)
        forward_loader = FakeConnector()

        runner_class(fake_transformation_config()).run(
            forward_extractor, forward_mapping, forward_loader
        )

        assert list(forward_loader.data) == [
            {"c": 2, "d": 5},
            {"c": 6, "d": 7},
            {"c": 10, "d": 9},
            {"c": 14, "d": 11},
        ]

        # reverse runner
        reverse_mapping = FileMapping(
            fake_transformation_config(
                {
                    "transformations": {
                        "ACC": {
                            "input_format": {
                                "name": "B",
                                "version": "1",
                            },
                            "output_format": {
                                "name": "A",
                                "version": "1",
                            },
                        }
                    }
                }
            ),
            "ACC",
            standard_search_path=search,
            search_working_dir=False,
        )
        reverse_extractor = forward_loader
        reverse_loader = FakeConnector()

        runner_class(fake_transformation_config()).run(
            reverse_extractor, reverse_mapping, reverse_loader
        )

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
                "file_type": "ACC",
                "input_format": {"name": "A", "version": "1"},
                "output_format": {"name": "B", "version": "1"},
                "forward": {
                    "transform": {
                        "c": [{"transformation": "a * 2"}],
                        "d": [{"transformation": "b + 3"}],
                    }
                },
                "reverse": {
                    "transform": {
                        "a": [{"transformation": "c / 2"}],
                        "b": [{"transformation": "d - 3"}],
                    }
                },
            },
        )
        write_yaml(
            os.path.join(search, "B-C.yml"),
            {
                "file_type": "ACC",
                "input_format": {"name": "B", "version": "1"},
                "output_format": {"name": "C", "version": "1"},
                "forward": {
                    "transform": {
                        "e": [{"transformation": "c * 3"}],
                        "f": [{"transformation": "d + 4"}],
                    }
                },
                "reverse": {
                    "transform": {
                        "c": [{"transformation": "e / 3"}],
                        "d": [{"transformation": "f - 4"}],
                    }
                },
            },
        )

        # run forward
        forward_mapping = FileMapping(
            fake_transformation_config(
                {
                    "transformations": {
                        "ACC": {
                            "input_format": {
                                "name": "A",
                                "version": "1",
                            },
                            "output_format": {
                                "name": "C",
                                "version": "1",
                            },
                        }
                    }
                }
            ),
            "ACC",
            standard_search_path=search,
            search_working_dir=False,
        )
        forward_extractor = FakeConnector(data=input_data)
        forward_loader = FakeConnector()

        runner_class(fake_transformation_config()).run(
            forward_extractor, forward_mapping, forward_loader
        )

        assert list(forward_loader.data) == [
            {"e": 6, "f": 9},
            {"e": 18, "f": 11},
            {"e": 30, "f": 13},
            {"e": 42, "f": 15},
        ]

        # reverse runner
        reverse_mapping = FileMapping(
            fake_transformation_config(
                {
                    "transformations": {
                        "ACC": {
                            "input_format": {
                                "name": "C",
                                "version": "1",
                            },
                            "output_format": {
                                "name": "A",
                                "version": "1",
                            },
                        }
                    }
                }
            ),
            "ACC",
            standard_search_path=search,
            search_working_dir=False,
        )
        reverse_extractor = forward_loader
        reverse_loader = FakeConnector()

        runner_class(fake_transformation_config()).run(
            reverse_extractor, reverse_mapping, reverse_loader
        )

        assert list(reverse_loader.data) == input_data


@given(runner_class=runners())
@settings(deadline=None)
def test_multiple_transforms_could_apply___first_is_applied(
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
                "file_type": "ACC",
                "input_format": {"name": "A", "version": "1"},
                "output_format": {"name": "B", "version": "1"},
                "forward": {
                    "transform": {
                        "c": [
                            {"transformation": "a * 2"},
                            {"transformation": "a * 4"},
                        ],
                        "d": [{"transformation": "b + 3"}],
                    }
                },
                "reverse": {
                    "transform": {
                        "a": [{"transformation": "c / 2"}],
                        "b": [{"transformation": "d - 3"}],
                    }
                },
            },
        )

        # run forward
        forward_mapping = FileMapping(
            fake_transformation_config(),
            "ACC",
            standard_search_path=search,
            search_working_dir=False,
        )
        forward_extractor = FakeConnector(data=input_data)
        forward_loader = FakeConnector()

        runner_class(fake_transformation_config()).run(
            forward_extractor, forward_mapping, forward_loader
        )

        assert list(forward_loader.data) == [
            {"c": 2, "d": 5},
            {"c": 6, "d": 7},
            {"c": 10, "d": 9},
            {"c": 14, "d": 11},
        ]

        # reverse runner
        reverse_mapping = FileMapping(
            fake_transformation_config(
                {
                    "transformations": {
                        "ACC": {
                            "input_format": {
                                "name": "B",
                                "version": "1",
                            },
                            "output_format": {
                                "name": "A",
                                "version": "1",
                            },
                        }
                    }
                }
            ),
            "ACC",
            standard_search_path=search,
            search_working_dir=False,
        )
        reverse_extractor = forward_loader
        reverse_loader = FakeConnector()

        runner_class(fake_transformation_config()).run(
            reverse_extractor, reverse_mapping, reverse_loader
        )

        assert list(reverse_loader.data) == input_data


@given(runner_class=runners())
@settings(deadline=None)
def test_row_is_value___value_is_set_on_all_columns(
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
                "file_type": "ACC",
                "input_format": {"name": "A", "version": "1"},
                "output_format": {"name": "B", "version": "1"},
                "forward": {
                    "transform": {
                        "c": [{"transformation": "a * 2"}],
                        "d": [{"transformation": "b + 3"}],
                        "e": [{"transformation": "'foo'"}],
                    }
                },
                "reverse": {
                    "transform": {
                        "a": [{"transformation": "c / 2"}],
                        "b": [{"transformation": "d - 3"}],
                    }
                },
            },
        )

        # run forward
        forward_mapping = FileMapping(
            fake_transformation_config(),
            "ACC",
            standard_search_path=search,
            search_working_dir=False,
        )
        forward_extractor = FakeConnector(data=input_data)
        forward_loader = FakeConnector()

        runner_class(fake_transformation_config()).run(
            forward_extractor, forward_mapping, forward_loader
        )

        assert list(forward_loader.data) == [
            {"c": 2, "d": 5, "e": "foo"},
            {"c": 6, "d": 7, "e": "foo"},
            {"c": 10, "d": 9, "e": "foo"},
            {"c": 14, "d": 11, "e": "foo"},
        ]

        # reverse runner
        reverse_mapping = FileMapping(
            fake_transformation_config(
                {
                    "transformations": {
                        "ACC": {
                            "input_format": {
                                "name": "B",
                                "version": "1",
                            },
                            "output_format": {
                                "name": "A",
                                "version": "1",
                            },
                        }
                    }
                }
            ),
            "ACC",
            standard_search_path=search,
            search_working_dir=False,
        )
        reverse_extractor = forward_loader
        reverse_loader = FakeConnector()

        runner_class(fake_transformation_config()).run(
            reverse_extractor, reverse_mapping, reverse_loader
        )

        assert list(reverse_loader.data) == input_data


def test_base_transform_raises():
    with pytest.raises(NotImplementedError):
        BaseRunner(fake_transformation_config()).transform(
            BaseConnector(fake_transformation_config()),
            BaseMapping(
                fake_transformation_config(),
                "ACC",
            ),
        )


@pytest.mark.asyncio
async def test_base_async_transform_raises():
    with pytest.raises(NotImplementedError):
        [
            row
            async for row in BaseAsyncRunner(
                fake_transformation_config()
            ).transform(
                BaseConnector(fake_transformation_config()),
                BaseMapping(
                    fake_transformation_config(),
                    "ACC",
                ),
            )
        ]
