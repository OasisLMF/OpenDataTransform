import os
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

import pytest
from hypothesis import given
from hypothesis.strategies import booleans, lists, sampled_from, text

from converter.files.yaml import write_yaml
from converter.mapping.base import (
    ColumnConversion,
    MappingFormat,
    TransformationEntry,
)
from converter.mapping.errors import NoConversionPathError
from converter.mapping.file import (
    FileMapping,
    FileMappingSpec,
    InvalidMappingFile,
)


#
# MappingFile tests
#
from tests.config.fakes import fake_transformation_config


def test_mapping_file_has_no_base___mapping_is_loaded_as_expected():
    config_path = os.path.abspath("config.yml")
    config = {
        "file_type": "ACC",
        "input_format": {"name": "foo", "version": "1"},
        "output_format": {"name": "bar", "version": "1"},
        "forward": {"transform": {"a": [{"transformation": "b"}]}},
        "reverse": {"transform": {"b": [{"transformation": "a"}]}},
    }
    all_found_configs = {config_path: config}

    mapping = FileMappingSpec(
        config_path, config, all_found_configs, [os.path.abspath(".")]
    )

    assert mapping.path == config_path
    assert mapping.file_type == "ACC"
    assert mapping.input_format == MappingFormat(name="foo", version="1")
    assert mapping.output_format == MappingFormat(name="bar", version="1")
    assert mapping.forward.transformation_set == {
        "a": [TransformationEntry(transformation="b")]
    }
    assert mapping.reverse.transformation_set == {
        "b": [TransformationEntry(transformation="a")]
    }
    assert all_found_configs[config_path] == mapping


def test_mapping_is_missing_file_type___error_is_raised():
    config_path = os.path.abspath("config.yml")
    config = {
        "input_format": {"name": "foo", "version": "1"},
        "output_format": {"name": "bar", "version": "1"},
        "forward": {"transform": {"a": [{"transformation": "b"}]}},
        "reverse": {"transform": {"b": [{"transformation": "a"}]}},
    }
    all_found_configs = {config_path: config}

    with pytest.raises(
        InvalidMappingFile,
        match=f"{config_path}: file_type not found in the config file or "
        f"its bases",
    ):
        FileMappingSpec(
            config_path, config, all_found_configs, [os.path.abspath(".")]
        )


def test_mapping_is_missing_input_format___error_is_raised():
    config_path = os.path.abspath("config.yml")
    config = {
        "file_type": "ACC",
        "output_format": {"name": "bar", "version": "1"},
        "forward": {"transform": {"a": [{"transformation": "b"}]}},
        "reverse": {"transform": {"b": [{"transformation": "a"}]}},
    }
    all_found_configs = {config_path: config}

    with pytest.raises(
        InvalidMappingFile,
        match=f"{config_path}: input_format not found in the config file or "
        f"its bases",
    ):
        FileMappingSpec(
            config_path, config, all_found_configs, [os.path.abspath(".")]
        )


def test_mapping_is_missing_output_format___error_is_raised():
    config_path = os.path.abspath("config.yml")
    config = {
        "file_type": "ACC",
        "input_format": {"name": "foo", "version": "1"},
        "forward": {"transform": {"a": [{"transformation": "b"}]}},
        "reverse": {"transform": {"b": [{"transformation": "a"}]}},
    }
    all_found_configs = {config_path: config}

    with pytest.raises(
        InvalidMappingFile,
        match=f"{config_path}: output_format not found in the config file or "
        f"its bases",
    ):
        FileMappingSpec(
            config_path, config, all_found_configs, [os.path.abspath(".")]
        )


def test_base_cannot_be_found___error_is_raised():
    config_path = os.path.abspath("config.yml")
    config = {
        "bases": ["missingBase"],
        "file_type": "ACC",
        "input_format": {"name": "foo", "version": "1"},
        "output_format": {"name": "bar", "version": "1"},
        "forward": {"transform": {"a": [{"transformation": "b"}]}},
        "reverse": {"transform": {"b": [{"transformation": "a"}]}},
    }
    all_found_configs = {config_path: config}

    with pytest.raises(
        InvalidMappingFile,
        match=(
            rf"{config_path}: Could not find base mapping file \(missingBase\)"
        ),
    ):
        FileMappingSpec(
            config_path, config, all_found_configs, [os.path.abspath(".")]
        )


def test_mapping_has_base_and_no_input_format___base_format_is_used():
    base_path = os.path.abspath("base.yml")
    base_config = {
        "file_type": "ACC",
        "input_format": {"name": "foo", "version": "1"},
        "output_format": {"name": "far", "version": "1"},
        "forward": {"transform": {"a": [{"transformation": "c"}]}},
        "reverse": {"transform": {"b": [{"transformation": "d"}]}},
    }

    config_path = os.path.abspath("config.yml")
    config = {
        "bases": ["base"],
        "output_format": {"name": "bar", "version": "1"},
        "forward": {"transform": {"a": [{"transformation": "b"}]}},
        "reverse": {"transform": {"b": [{"transformation": "a"}]}},
    }
    all_found_configs = {config_path: config, base_path: base_config}

    mapping = FileMappingSpec(
        config_path, config, all_found_configs, [os.path.abspath(".")]
    )

    assert mapping.path == config_path
    assert mapping.file_type == "ACC"
    assert mapping.input_format == MappingFormat(name="foo", version="1")
    assert mapping.output_format == MappingFormat(name="bar", version="1")
    assert mapping.forward.transformation_set == {
        "a": [TransformationEntry(transformation="b")]
    }
    assert mapping.reverse.transformation_set == {
        "b": [TransformationEntry(transformation="a")]
    }
    assert all_found_configs[config_path] == mapping


def test_mapping_has_base_and_no_bar_format___base_format_is_used():
    base_path = os.path.abspath("base.yml")
    base_config = {
        "file_type": "ACC",
        "input_format": {"name": "boo", "version": "1"},
        "output_format": {"name": "bar", "version": "1"},
        "forward": {"transform": {"a": [{"transformation": "c"}]}},
        "reverse": {"transform": {"b": [{"transformation": "d"}]}},
    }

    config_path = os.path.abspath("config.yml")
    config = {
        "bases": ["base"],
        "input_format": {"name": "foo", "version": "1"},
        "forward": {"transform": {"a": [{"transformation": "b"}]}},
        "reverse": {"transform": {"b": [{"transformation": "a"}]}},
    }
    all_found_configs = {config_path: config, base_path: base_config}

    mapping = FileMappingSpec(
        config_path, config, all_found_configs, [os.path.abspath(".")]
    )

    assert mapping.path == config_path
    assert mapping.file_type == "ACC"
    assert mapping.input_format == MappingFormat(name="foo", version="1")
    assert mapping.output_format == MappingFormat(name="bar", version="1")
    assert mapping.forward.transformation_set == {
        "a": [TransformationEntry(transformation="b")]
    }
    assert mapping.reverse.transformation_set == {
        "b": [TransformationEntry(transformation="a")]
    }
    assert all_found_configs[config_path] == mapping


def test_mapping_has_base___forward_transforms_are_merged():
    base_path = os.path.abspath("base.yml")
    base_config = {
        "file_type": "ACC",
        "input_format": {"name": "boo", "version": "1"},
        "output_format": {"name": "bar", "version": "1"},
        "forward": {"transform": {"c": [{"transformation": "d"}]}},
        "reverse": {"transform": {"b": [{"transformation": "d"}]}},
    }

    config_path = os.path.abspath("config.yml")
    config = {
        "bases": ["base"],
        "input_format": {"name": "foo", "version": "1"},
        "forward": {"transform": {"a": [{"transformation": "b"}]}},
        "reverse": {"transform": {"b": [{"transformation": "a"}]}},
    }
    all_found_configs = {config_path: config, base_path: base_config}

    mapping = FileMappingSpec(
        config_path, config, all_found_configs, [os.path.abspath(".")]
    )

    assert mapping.path == config_path
    assert mapping.file_type == "ACC"
    assert mapping.input_format == MappingFormat(name="foo", version="1")
    assert mapping.output_format == MappingFormat(name="bar", version="1")
    assert mapping.forward.transformation_set == {
        "a": [TransformationEntry(transformation="b")],
        "c": [TransformationEntry(transformation="d")],
    }
    assert mapping.reverse.transformation_set == {
        "b": [TransformationEntry(transformation="a")]
    }
    assert all_found_configs[config_path] == mapping


def test_mapping_has_base___reverse_transforms_are_merged():
    base_path = os.path.abspath("base.yml")
    base_config = {
        "file_type": "ACC",
        "input_format": {"name": "boo", "version": "1"},
        "output_format": {"name": "bar", "version": "1"},
        "forward": {"transform": {"a": [{"transformation": "d"}]}},
        "reverse": {
            "transform": {
                "b": [TransformationEntry(transformation="d")],
                "d": [TransformationEntry(transformation="c")],
            }
        },
    }

    config_path = os.path.abspath("config.yml")
    config = {
        "bases": ["base"],
        "input_format": {"name": "foo", "version": "1"},
        "forward": {"transform": {"a": [{"transformation": "b"}]}},
        "reverse": {"transform": {"b": [{"transformation": "a"}]}},
    }
    all_found_configs = {config_path: config, base_path: base_config}

    mapping = FileMappingSpec(
        config_path, config, all_found_configs, [os.path.abspath(".")]
    )

    assert mapping.path == config_path
    assert mapping.file_type == "ACC"
    assert mapping.input_format == MappingFormat(name="foo", version="1")
    assert mapping.output_format == MappingFormat(name="bar", version="1")
    assert mapping.forward.transformation_set == {
        "a": [TransformationEntry(transformation="b")],
    }
    assert mapping.reverse.transformation_set == {
        "b": [TransformationEntry(transformation="a")],
        "d": [TransformationEntry(transformation="c")],
    }
    assert all_found_configs[config_path] == mapping


@given(ext=sampled_from(["yml", "yaml"]))
def test_mapping_has_path_base___base_is_used(ext):
    base_path = os.path.abspath(f"base.{ext}")
    base_config = {
        "file_type": "ACC",
        "input_format": {"name": "foo", "version": "1"},
        "output_format": {"name": "far", "version": "1"},
        "forward": {"transform": {"a": [{"transformation": "c"}]}},
        "reverse": {"transform": {"b": [{"transformation": "d"}]}},
    }

    config_path = os.path.abspath("config.yml")
    config = {
        "bases": [f"base.{ext}"],
        "output_format": {"name": "bar", "version": "1"},
        "forward": {"transform": {"a": [{"transformation": "b"}]}},
        "reverse": {"transform": {"b": [{"transformation": "a"}]}},
    }
    all_found_configs = {config_path: config, base_path: base_config}

    mapping = FileMappingSpec(
        config_path, config, all_found_configs, [os.path.abspath(".")]
    )

    assert mapping.path == config_path
    assert mapping.file_type == "ACC"
    assert mapping.input_format == MappingFormat(name="foo", version="1")
    assert mapping.output_format == MappingFormat(name="bar", version="1")
    assert mapping.forward.transformation_set == {
        "a": [TransformationEntry(transformation="b")]
    }
    assert mapping.reverse.transformation_set == {
        "b": [TransformationEntry(transformation="a")]
    }
    assert all_found_configs[config_path] == mapping


def test_mapping_has_multiple_base___later_bases_are_preferred():
    first_base_path = os.path.abspath("first.yml")
    first_base_config = {
        "file_type": "ACC",
        "input_format": {"name": "boo", "version": "1"},
        "output_format": {"name": "bash", "version": "1"},
        "forward": {
            "transform": {
                "a": [TransformationEntry(transformation="b")],
                "x": [TransformationEntry(transformation="y")],
            }
        },
        "reverse": {
            "transform": {
                "b": [TransformationEntry(transformation="a")],
                "y": [TransformationEntry(transformation="x")],
            }
        },
    }

    second_base_path = os.path.abspath("second.yaml")
    second_base_config = {
        "file_type": "ACC",
        "input_format": {"name": "fish", "version": "1"},
        "output_format": {"name": "far", "version": "1"},
        "forward": {
            "transform": {
                "c": [TransformationEntry(transformation="d")],
                "x": [TransformationEntry(transformation="z")],
            }
        },
        "reverse": {
            "transform": {
                "d": [TransformationEntry(transformation="c")],
                "z": [TransformationEntry(transformation="x")],
            }
        },
    }

    config_path = os.path.abspath("config.yml")
    config = {
        "bases": ["first", "second"],
        "input_format": {"name": "foo", "version": "1"},
        "output_format": {"name": "bar", "version": "1"},
        "forward": {"transform": {"e": [{"transformation": "f"}]}},
        "reverse": {"transform": {"f": [{"transformation": "e"}]}},
    }
    all_found_configs = {
        config_path: config,
        first_base_path: first_base_config,
        second_base_path: second_base_config,
    }

    mapping = FileMappingSpec(
        config_path, config, all_found_configs, [os.path.abspath(".")]
    )

    assert mapping.path == config_path
    assert mapping.file_type == "ACC"
    assert mapping.input_format == MappingFormat(name="foo", version="1")
    assert mapping.output_format == MappingFormat(name="bar", version="1")
    assert mapping.forward.transformation_set == {
        "a": [TransformationEntry(transformation="b")],
        "c": [TransformationEntry(transformation="d")],
        "e": [TransformationEntry(transformation="f")],
        "x": [TransformationEntry(transformation="z")],
    }
    assert mapping.reverse.transformation_set == {
        "b": [TransformationEntry(transformation="a")],
        "d": [TransformationEntry(transformation="c")],
        "f": [TransformationEntry(transformation="e")],
        "y": [TransformationEntry(transformation="x")],
        "z": [TransformationEntry(transformation="x")],
    }
    assert all_found_configs[config_path] == mapping


def test_mapping_has_base_with_base___grand_parent_bases_are_loaded():
    first_base_path = os.path.abspath("first.yml")
    first_base_config = {
        "file_type": "ACC",
        "input_format": {"name": "boo", "version": "1"},
        "output_format": {"name": "bash", "version": "1"},
        "forward": {
            "transform": {
                "a": [TransformationEntry(transformation="b")],
                "x": [TransformationEntry(transformation="y")],
            }
        },
        "reverse": {
            "transform": {
                "b": [TransformationEntry(transformation="a")],
                "y": [TransformationEntry(transformation="x")],
            }
        },
    }

    second_base_path = os.path.abspath("second.yaml")
    second_base_config = {
        "bases": ["first"],
        "output_format": {"name": "far", "version": "1"},
        "forward": {
            "transform": {
                "c": [TransformationEntry(transformation="d")],
                "x": [TransformationEntry(transformation="z")],
            }
        },
        "reverse": {
            "transform": {
                "d": [TransformationEntry(transformation="c")],
                "z": [TransformationEntry(transformation="x")],
            }
        },
    }

    config_path = os.path.abspath("config.yml")
    config = {
        "bases": ["second"],
        "input_format": {"name": "foo", "version": "1"},
        "output_format": {"name": "bar", "version": "1"},
        "forward": {"transform": {"e": [{"transformation": "f"}]}},
        "reverse": {"transform": {"f": [{"transformation": "e"}]}},
    }
    all_found_configs = {
        config_path: config,
        first_base_path: first_base_config,
        second_base_path: second_base_config,
    }

    mapping = FileMappingSpec(
        config_path, config, all_found_configs, [os.path.abspath(".")]
    )

    assert mapping.path == config_path
    assert mapping.file_type == "ACC"
    assert mapping.input_format == MappingFormat(name="foo", version="1")
    assert mapping.output_format == MappingFormat(name="bar", version="1")
    assert mapping.forward.transformation_set == {
        "a": [TransformationEntry(transformation="b")],
        "c": [TransformationEntry(transformation="d")],
        "e": [TransformationEntry(transformation="f")],
        "x": [TransformationEntry(transformation="z")],
    }
    assert mapping.reverse.transformation_set == {
        "b": [TransformationEntry(transformation="a")],
        "d": [TransformationEntry(transformation="c")],
        "f": [TransformationEntry(transformation="e")],
        "y": [TransformationEntry(transformation="x")],
        "z": [TransformationEntry(transformation="x")],
    }
    assert all_found_configs[config_path] == mapping


def test_mapping_has_base_in_different_search_path___bases_is_loaded():
    other_search_path = "/somepath/"
    base_path = os.path.join(other_search_path, "base.yml")
    base_config = {
        "file_type": "ACC",
        "input_format": {"name": "boo", "version": "1"},
        "output_format": {"name": "bar", "version": "1"},
        "forward": {"transform": {"a": [{"transformation": "d"}]}},
        "reverse": {
            "transform": {
                "b": [TransformationEntry(transformation="d")],
                "d": [TransformationEntry(transformation="c")],
            }
        },
    }

    config_path = os.path.abspath("config.yml")
    config = {
        "bases": ["base"],
        "input_format": {"name": "foo", "version": "1"},
        "forward": {"transform": {"a": [{"transformation": "b"}]}},
        "reverse": {"transform": {"b": [{"transformation": "a"}]}},
    }
    all_found_configs = {config_path: config, base_path: base_config}

    mapping = FileMappingSpec(
        config_path,
        config,
        all_found_configs,
        [os.path.abspath("."), other_search_path],
    )

    assert mapping.path == config_path
    assert mapping.file_type == "ACC"
    assert mapping.input_format == MappingFormat(name="foo", version="1")
    assert mapping.output_format == MappingFormat(name="bar", version="1")
    assert mapping.forward.transformation_set == {
        "a": [TransformationEntry(transformation="b")],
    }
    assert mapping.reverse.transformation_set == {
        "b": [TransformationEntry(transformation="a")],
        "d": [TransformationEntry(transformation="c")],
    }
    assert all_found_configs[config_path] == mapping


def test_mapping_file_has_forward_transform___can_run_forward_is_true():
    config_path = os.path.abspath("config.yml")
    config = {
        "file_type": "ACC",
        "input_format": {"name": "foo", "version": "1"},
        "output_format": {"name": "bar", "version": "1"},
        "forward": {"transform": {"a": [{"transformation": "b"}]}},
        "reverse": {"transform": {"b": [{"transformation": "a"}]}},
    }
    all_found_configs = {config_path: config}

    mapping = FileMappingSpec(
        config_path, config, all_found_configs, [os.path.abspath(".")]
    )

    assert mapping.can_run_forwards is True


def test_mapping_file_has_no_forward_transform___can_run_forward_is_false():
    config_path = os.path.abspath("config.yml")
    config = {
        "file_type": "ACC",
        "input_format": {"name": "foo", "version": "1"},
        "output_format": {"name": "bar", "version": "1"},
        "reverse": {"transform": {"b": [{"transformation": "a"}]}},
    }
    all_found_configs = {config_path: config}

    mapping = FileMappingSpec(
        config_path, config, all_found_configs, [os.path.abspath(".")]
    )

    assert mapping.can_run_forwards is False


def test_mapping_file_has_reverse_transform___can_run_in_reverse_is_true():
    config_path = os.path.abspath("config.yml")
    config = {
        "file_type": "ACC",
        "input_format": {"name": "foo", "version": "1"},
        "output_format": {"name": "bar", "version": "1"},
        "forward": {"transform": {"a": [{"transformation": "b"}]}},
        "reverse": {"transform": {"b": [{"transformation": "a"}]}},
    }
    all_found_configs = {config_path: config}

    mapping = FileMappingSpec(
        config_path, config, all_found_configs, [os.path.abspath(".")]
    )

    assert mapping.can_run_in_reverse is True


def test_mapping_file_has_no_reverse_transform___can_run_in_reverse_is_false():
    config_path = os.path.abspath("config.yml")
    config = {
        "file_type": "ACC",
        "input_format": {"name": "foo", "version": "1"},
        "output_format": {"name": "bar", "version": "1"},
        "forward": {"transform": {"a": [{"transformation": "b"}]}},
    }
    all_found_configs = {config_path: config}

    mapping = FileMappingSpec(
        config_path, config, all_found_configs, [os.path.abspath(".")]
    )

    assert mapping.can_run_in_reverse is False


#
# FileMapping tests
#


@given(paths=lists(text()))
def test_standard_and_current_path_is_added_to_the_abs_search_paths(paths):
    package_root_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
        )
    )

    config = fake_transformation_config()
    mapping = FileMapping(
        config,
        file_type="ACC",
        input_format=MappingFormat(name="A", version="1"),
        output_format=MappingFormat(name="B", version="1"),
        search_paths=paths,
    )

    assert mapping.search_paths == [
        os.path.abspath("."),
        os.path.dirname(config.path),
        *(os.path.abspath(p) for p in paths),
        os.path.join(
            package_root_dir,
            "converter",
            "data",
            "mappings",
        ),
    ]


def test_multiple_search_paths_contain_files___all_are_loaded():
    with TemporaryDirectory() as first, TemporaryDirectory() as second:
        write_yaml(
            os.path.join(first, "A-B.yml"),
            {
                "file_type": "ACC",
                "input_format": {"name": "A", "version": "1"},
                "output_format": {"name": "B", "version": "1"},
            },
        )
        write_yaml(
            os.path.join(first, "B-C.yaml"),
            {
                "file_type": "ACC",
                "input_format": {"name": "B", "version": "1"},
                "output_format": {"name": "C", "version": "1"},
            },
        )
        write_yaml(
            os.path.join(second, "C-D.yml"),
            {
                "file_type": "ACC",
                "input_format": {"name": "C", "version": "1"},
                "output_format": {"name": "D", "version": "1"},
            },
        )
        write_yaml(
            os.path.join(second, "D-E.yaml"),
            {
                "file_type": "ACC",
                "input_format": {"name": "D", "version": "1"},
                "output_format": {"name": "E", "version": "1"},
            },
        )

        mapping = FileMapping(
            fake_transformation_config(),
            file_type="ACC",
            input_format=MappingFormat(name="A", version="1"),
            output_format=MappingFormat(name="B", version="1"),
            search_paths=[first],
            standard_search_path=second,
        )

        loaded = {c.path: c for c in mapping.mapping_specs}

        assert loaded[
            os.path.join(first, "A-B.yml")
        ].input_format == MappingFormat(name="A", version="1")
        assert loaded[
            os.path.join(first, "A-B.yml")
        ].output_format == MappingFormat(name="B", version="1")

        assert loaded[
            os.path.join(first, "B-C.yaml")
        ].input_format == MappingFormat(name="B", version="1")
        assert loaded[
            os.path.join(first, "B-C.yaml")
        ].output_format == MappingFormat(name="C", version="1")

        assert loaded[
            os.path.join(second, "C-D.yml")
        ].input_format == MappingFormat(name="C", version="1")
        assert loaded[
            os.path.join(second, "C-D.yml")
        ].output_format == MappingFormat(name="D", version="1")

        assert loaded[
            os.path.join(second, "D-E.yaml")
        ].input_format == MappingFormat(name="D", version="1")
        assert loaded[
            os.path.join(second, "D-E.yaml")
        ].output_format == MappingFormat(name="E", version="1")


def test_yaml_files_with_non_mapping_fields_in_search_paths_are_excluded():
    with TemporaryDirectory() as first:
        write_yaml(
            os.path.join(first, "A-B.yml"),
            {
                "file_type": "ACC",
                "input_format": {"name": "A", "version": "1"},
                "output_format": {"name": "B", "version": "1"},
            },
        )
        write_yaml(
            os.path.join(first, "B-C.yaml"),
            {
                "file_type": "ACC",
                "input_format": {"name": "B", "version": "1"},
                "output_format": {"name": "C", "version": "1"},
            },
        )
        write_yaml(os.path.join(first, "other.yaml"), {"other_field": "foo"})

        mapping = FileMapping(
            fake_transformation_config(),
            file_type="ACC",
            input_format=MappingFormat(name="A", version="1"),
            output_format=MappingFormat(name="B", version="1"),
            standard_search_path=first,
        )

        loaded = {c.path: c for c in mapping.mapping_specs}

        assert os.path.join(first, "A-B.yml") in loaded
        assert os.path.join(first, "B-C.yaml") in loaded
        assert os.path.join(first, "other.yaml") not in loaded


def test_invalid_mapping_exists___its_excluded_and_warning_is_written():
    with TemporaryDirectory() as first:
        write_yaml(
            os.path.join(first, "A-B.yml"),
            {
                "file_type": "ACC",
                "input_format": {"name": "A", "version": "1"},
                "output_format": {"name": "B", "version": "1"},
            },
        )
        write_yaml(
            os.path.join(first, "B-C.yaml"),
            {
                "file_type": "ACC",
                "input_format": {"name": "B", "version": "1"},
                "output_format": {"name": "C", "version": "1"},
            },
        )
        write_yaml(
            os.path.join(first, "invalid.yaml"),
            {
                "file_type": "ACC",
                "output_format": {"name": "D", "version": "1"},
            },
        )

        log_mock = Mock()
        with patch("converter.mapping.file.get_logger", return_value=log_mock):
            mapping = FileMapping(
                fake_transformation_config(),
                file_type="ACC",
                input_format=MappingFormat(name="A", version="1"),
                output_format=MappingFormat(name="B", version="1"),
                standard_search_path=first,
            )

            loaded = {c.path: c for c in mapping.mapping_specs}

            expected_error = InvalidMappingFile(
                "input_format not found in the config file or its bases",
                os.path.join(first, "invalid.yaml"),
            )

            log_mock.warning.assert_called_once_with(str(expected_error))
            assert os.path.join(first, "A-B.yml") in loaded
            assert os.path.join(first, "B-C.yaml") in loaded
            assert os.path.join(first, "invalid.yaml") not in loaded


def test_mapping_file_has_forward_and_reverse_trans___both_paths_are_valid():
    with TemporaryDirectory() as first:
        write_yaml(
            os.path.join(first, "A-B.yml"),
            {
                "file_type": "ACC",
                "input_format": {"name": "A", "version": "1"},
                "output_format": {"name": "B", "version": "1"},
                "forward": {"transform": {"b": [{"transformation": "a"}]}},
                "reverse": {"transform": {"a": [{"transformation": "b"}]}},
            },
        )

        ab_mapping = FileMapping(
            fake_transformation_config(),
            file_type="ACC",
            standard_search_path=first,
            search_working_dir=False,
        )

        assert [
            m.transformation_set for m in ab_mapping.get_transformations()
        ] == [{"b": [TransformationEntry(transformation="a", when="True")]}]

        ba_mapping = FileMapping(
            fake_transformation_config({
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
                }}
            ),
            "ACC",
            standard_search_path=first,
            search_working_dir=False,
        )

        assert [
            m.transformation_set for m in ba_mapping.get_transformations()
        ] == [{"a": [TransformationEntry(transformation="b", when="True")]}]


def test_mapping_file_has_no_reverse___reverse_path_is_not_possible():
    with TemporaryDirectory() as first:
        write_yaml(
            os.path.join(first, "A-B.yml"),
            {
                "file_type": "ACC",
                "input_format": {"name": "A", "version": "1"},
                "output_format": {"name": "B", "version": "1"},
                "forward": {"transform": {"b": [{"transformation": "a"}]}},
            },
        )

        ab_mapping = FileMapping(
            fake_transformation_config(),
            file_type="ACC",
            input_format=MappingFormat(name="A", version="1"),
            output_format=MappingFormat(name="B", version="1"),
            standard_search_path=first,
            search_working_dir=False,
        )

        assert [
            m.transformation_set for m in ab_mapping.get_transformations()
        ] == [{"b": [TransformationEntry(transformation="a", when="True")]}]

        with pytest.raises(
            NoConversionPathError,
            match="No conversion path from B v1 to A v1.",
        ):
            ba_mapping = FileMapping(
                fake_transformation_config(),
                file_type="ACC",
                input_format=MappingFormat(name="B", version="1"),
                output_format=MappingFormat(name="A", version="1"),
                standard_search_path=first,
                search_working_dir=False,
            )

            ba_mapping.get_transformations()


def test_mapping_file_has_no_forward___forward_path_is_not_possible():
    with TemporaryDirectory() as first:
        write_yaml(
            os.path.join(first, "A-B.yml"),
            {
                "file_type": "ACC",
                "input_format": {"name": "A", "version": "1"},
                "output_format": {"name": "B", "version": "1"},
                "reverse": {"transform": {"a": [{"transformation": "b"}]}},
            },
        )

        with pytest.raises(
            NoConversionPathError,
            match="No conversion path from A v1 to B v1.",
        ):
            ab_mapping = FileMapping(
                fake_transformation_config(),
                file_type="ACC",
                input_format=MappingFormat(name="A", version="1"),
                output_format=MappingFormat(name="B", version="1"),
                standard_search_path=first,
                search_working_dir=False,
            )

            assert [
                m.transformation_set for m in ab_mapping.get_transformations()
            ] == [
                {"b": [TransformationEntry(transformation="a", when="True")]},
            ]

        ba_mapping = FileMapping(
            fake_transformation_config(),
            file_type="ACC",
            input_format=MappingFormat(name="B", version="1"),
            output_format=MappingFormat(name="A", version="1"),
            standard_search_path=first,
            search_working_dir=False,
        )

        assert [
            m.transformation_set for m in ba_mapping.get_transformations()
        ] == [{"a": [TransformationEntry(transformation="b")]}]


def test_forward_is_provided_in_preferred_directory___forward_from_preferred():
    with TemporaryDirectory() as first, TemporaryDirectory() as second:
        write_yaml(
            os.path.join(first, "A-B.yml"),
            {
                "file_type": "ACC",
                "input_format": {"name": "A", "version": "1"},
                "output_format": {"name": "B", "version": "1"},
                "forward": {"transform": {"b": [{"transformation": "a"}]}},
                "reverse": {"transform": {"a": [{"transformation": "b"}]}},
            },
        )
        write_yaml(
            os.path.join(second, "preferred.yml"),
            {
                "file_type": "ACC",
                "input_format": {"name": "A", "version": "1"},
                "output_format": {"name": "B", "version": "1"},
                "forward": {"transform": {"c": [{"transformation": "d"}]}},
            },
        )

        ab_mapping = FileMapping(
            fake_transformation_config(),
            file_type="ACC",
            input_format=MappingFormat(name="A", version="1"),
            output_format=MappingFormat(name="B", version="1"),
            search_paths=[second],
            standard_search_path=first,
            search_working_dir=False,
        )

        assert [
            m.transformation_set for m in ab_mapping.get_transformations()
        ] == [{"c": [TransformationEntry(transformation="d", when="True")]}]

        ba_mapping = FileMapping(
            fake_transformation_config(),
            file_type="ACC",
            input_format=MappingFormat(name="B", version="1"),
            output_format=MappingFormat(name="A", version="1"),
            search_paths=[second],
            standard_search_path=first,
            search_working_dir=False,
        )

        assert [
            m.transformation_set for m in ba_mapping.get_transformations()
        ] == [{"a": [TransformationEntry(transformation="b", when="True")]}]


def test_reverse_is_provided_in_prefered_directory___reverse_from_preferred():
    with TemporaryDirectory() as first, TemporaryDirectory() as second:
        write_yaml(
            os.path.join(first, "A-B.yml"),
            {
                "file_type": "ACC",
                "input_format": {"name": "A", "version": "1"},
                "output_format": {"name": "B", "version": "1"},
                "forward": {"transform": {"b": [{"transformation": "a"}]}},
                "reverse": {"transform": {"a": [{"transformation": "b"}]}},
            },
        )
        write_yaml(
            os.path.join(second, "preferred.yml"),
            {
                "file_type": "ACC",
                "input_format": {"name": "A", "version": "1"},
                "output_format": {"name": "B", "version": "1"},
                "reverse": {"transform": {"c": [{"transformation": "d"}]}},
            },
        )

        ab_mapping = FileMapping(
            fake_transformation_config(),
            file_type="ACC",
            input_format=MappingFormat(name="A", version="1"),
            output_format=MappingFormat(name="B", version="1"),
            search_paths=[second],
            standard_search_path=first,
            search_working_dir=False,
        )

        assert [
            m.transformation_set for m in ab_mapping.get_transformations()
        ] == [{"b": [TransformationEntry(transformation="a", when="True")]}]

        ba_mapping = FileMapping(
            fake_transformation_config(),
            file_type="ACC",
            input_format=MappingFormat(name="B", version="1"),
            output_format=MappingFormat(name="A", version="1"),
            search_paths=[second],
            standard_search_path=first,
            search_working_dir=False,
        )

        assert [
            m.transformation_set for m in ba_mapping.get_transformations()
        ] == [{"c": [TransformationEntry(transformation="d", when="True")]}]


def test_multiple_steps_are_in_the_conversion___all_steps_are_returned():
    with TemporaryDirectory() as first:
        write_yaml(
            os.path.join(first, "A-B.yml"),
            {
                "file_type": "ACC",
                "input_format": {"name": "A", "version": "1"},
                "output_format": {"name": "B", "version": "1"},
                "forward": {"transform": {"b": [{"transformation": "a"}]}},
                "reverse": {"transform": {"a": [{"transformation": "b"}]}},
            },
        )
        write_yaml(
            os.path.join(first, "B-C.yml"),
            {
                "file_type": "ACC",
                "input_format": {"name": "B", "version": "1"},
                "output_format": {"name": "C", "version": "1"},
                "forward": {"transform": {"c": [{"transformation": "b"}]}},
                "reverse": {"transform": {"b": [{"transformation": "c"}]}},
            },
        )

        ab_mapping = FileMapping(
            fake_transformation_config(),
            file_type="ACC",
            input_format=MappingFormat(name="A", version="1"),
            output_format=MappingFormat(name="C", version="1"),
            standard_search_path=first,
            search_working_dir=False,
        )

        assert [
            m.transformation_set for m in ab_mapping.get_transformations()
        ] == [
            {"b": [TransformationEntry(transformation="a", when="True")]},
            {"c": [TransformationEntry(transformation="b", when="True")]},
        ]

        ba_mapping = FileMapping(
            fake_transformation_config(),
            "ACC",
            MappingFormat(name="C", version="1"),
            MappingFormat(name="A", version="1"),
            standard_search_path=first,
            search_working_dir=False,
        )

        assert [
            m.transformation_set for m in ba_mapping.get_transformations()
        ] == [
            {"b": [TransformationEntry(transformation="c", when="True")]},
            {"a": [TransformationEntry(transformation="b", when="True")]},
        ]


#
# Type loading
#


def test_types_have_null_values_set___processed_null_values_are_loaded():
    with TemporaryDirectory() as d:
        write_yaml(
            os.path.join(d, "A-B.yml"),
            {
                "file_type": "ACC",
                "input_format": {"name": "A", "version": "1"},
                "output_format": {"name": "B", "version": "1"},
                "forward": {
                    "transform": {"b": [{"transformation": "a"}]},
                    "types": {
                        "a": {
                            "type": "int",
                            "null_values": [0, "Null", "'NULL'"],
                        },
                    },
                },
            },
        )

        transformation = FileMapping(
            fake_transformation_config(),
            file_type="ACC",
            input_format=MappingFormat(name="A", version="1"),
            output_format=MappingFormat(name="B", version="1"),
            standard_search_path=d,
            search_working_dir=False,
        ).get_transformations()[0]

        assert transformation.types == {
            "a": ColumnConversion(
                type="int",
                nullable=True,
                null_values={0, None, "NULL"},
            ),
        }


@given(booleans())
def test_nullable_is_set___nullable_on_field_is_correct(nullable):
    with TemporaryDirectory() as d:
        write_yaml(
            os.path.join(d, "A-B.yml"),
            {
                "file_type": "ACC",
                "input_format": {"name": "A", "version": "1"},
                "output_format": {"name": "B", "version": "1"},
                "forward": {
                    "transform": {"b": [{"transformation": "a"}]},
                    "types": {
                        "a": {
                            "type": "int",
                            "null_values": [0, "Null", "'NULL'"],
                            "nullable": nullable,
                        },
                    },
                },
            },
        )

        transformation = FileMapping(
            fake_transformation_config(),
            file_type="ACC",
            input_format=MappingFormat(name="A", version="1"),
            output_format=MappingFormat(name="B", version="1"),
            standard_search_path=d,
            search_working_dir=False,
        ).get_transformations()[0]

        assert transformation.types == {
            "a": ColumnConversion(
                type="int",
                nullable=nullable,
                null_values={0, None, "NULL"},
            ),
        }


def test_null_values_are_set_on_forward___forward_values_are_loaded_into_col():
    with TemporaryDirectory() as d:
        write_yaml(
            os.path.join(d, "A-B.yml"),
            {
                "file_type": "ACC",
                "input_format": {"name": "A", "version": "1"},
                "output_format": {"name": "B", "version": "1"},
                "forward": {
                    "transform": {"b": [{"transformation": "a"}]},
                    "types": {"a": {"type": "int"}},
                    "null_values": [0, "Null", "'NULL'"],
                },
            },
        )

        transformation = FileMapping(
            fake_transformation_config(),
            file_type="ACC",
            input_format=MappingFormat(name="A", version="1"),
            output_format=MappingFormat(name="B", version="1"),
            standard_search_path=d,
            search_working_dir=False,
        ).get_transformations()[0]

        assert transformation.types == {
            "a": ColumnConversion(
                type="int",
                nullable=True,
                null_values={0, None, "NULL"},
            ),
        }
