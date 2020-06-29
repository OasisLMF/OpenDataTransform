import os
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest
import yaml
from hypothesis import given
from hypothesis.strategies import lists, sampled_from, text

from converter.mapping.file import FileMapping, InvalidMappingFile, MappingFile


def write_yaml(path, content):
    with open(path, "w") as f:
        yaml.dump(content, f)


#
# MappingFile tests
#


def test_mapping_file_has_no_base___mapping_is_loaded_as_expected():
    config_path = os.path.abspath("config.yml")
    config = {
        "input_format": "foo",
        "output_format": "bar",
        "forward_transform": {"a": {"transformation": "b"}},
        "reverse_transform": {"b": {"transformation": "a"}},
    }
    all_found_configs = {config_path: config}

    mapping = MappingFile(
        config_path, config, all_found_configs, [os.path.abspath(".")]
    )

    assert mapping.path == config_path
    assert mapping.input_format == "foo"
    assert mapping.output_format == "bar"
    assert mapping.forward_transform == {"a": {"transformation": "b"}}
    assert mapping.reverse_transform == {"b": {"transformation": "a"}}
    assert all_found_configs[config_path] == mapping


def test_mapping_is_missing_input_format___error_is_raised():
    config_path = os.path.abspath("config.yml")
    config = {
        "output_format": "bar",
        "forward_transform": {"a": {"transformation": "b"}},
        "reverse_transform": {"b": {"transformation": "a"}},
    }
    all_found_configs = {config_path: config}

    with pytest.raises(
        InvalidMappingFile,
        match=f"{config_path}: input_format not found in the config file or "
        f"its bases",
    ):
        MappingFile(
            config_path, config, all_found_configs, [os.path.abspath(".")]
        )


def test_mapping_is_missing_output_format___error_is_raised():
    config_path = os.path.abspath("config.yml")
    config = {
        "input_format": "foo",
        "forward_transform": {"a": {"transformation": "b"}},
        "reverse_transform": {"b": {"transformation": "a"}},
    }
    all_found_configs = {config_path: config}

    with pytest.raises(
        InvalidMappingFile,
        match=f"{config_path}: output_format not found in the config file or "
        f"its bases",
    ):
        MappingFile(
            config_path, config, all_found_configs, [os.path.abspath(".")]
        )


def test_base_cannot_be_found___error_is_raised():
    config_path = os.path.abspath("config.yml")
    config = {
        "bases": ["missingBase"],
        "input_format": "foo",
        "output_format": "bar",
        "forward_transform": {"a": {"transformation": "b"}},
        "reverse_transform": {"b": {"transformation": "a"}},
    }
    all_found_configs = {config_path: config}

    with pytest.raises(
        InvalidMappingFile,
        match=(
            rf"{config_path}: Could not find base mapping file \(missingBase\)"
        ),
    ):
        MappingFile(
            config_path, config, all_found_configs, [os.path.abspath(".")]
        )


def test_mapping_has_base_and_no_input_format___base_format_is_used():
    base_path = os.path.abspath("base.yml")
    base_config = {
        "input_format": "foo",
        "output_format": "far",
        "forward_transform": {"a": {"transformation": "c"}},
        "reverse_transform": {"b": {"transformation": "d"}},
    }

    config_path = os.path.abspath("config.yml")
    config = {
        "bases": ["base"],
        "output_format": "bar",
        "forward_transform": {"a": {"transformation": "b"}},
        "reverse_transform": {"b": {"transformation": "a"}},
    }
    all_found_configs = {config_path: config, base_path: base_config}

    mapping = MappingFile(
        config_path, config, all_found_configs, [os.path.abspath(".")]
    )

    assert mapping.path == config_path
    assert mapping.input_format == "foo"
    assert mapping.output_format == "bar"
    assert mapping.forward_transform == {"a": {"transformation": "b"}}
    assert mapping.reverse_transform == {"b": {"transformation": "a"}}
    assert all_found_configs[config_path] == mapping


def test_mapping_has_base_and_no_bar_format___base_format_is_used():
    base_path = os.path.abspath("base.yml")
    base_config = {
        "input_format": "boo",
        "output_format": "bar",
        "forward_transform": {"a": {"transformation": "c"}},
        "reverse_transform": {"b": {"transformation": "d"}},
    }

    config_path = os.path.abspath("config.yml")
    config = {
        "bases": ["base"],
        "input_format": "foo",
        "forward_transform": {"a": {"transformation": "b"}},
        "reverse_transform": {"b": {"transformation": "a"}},
    }
    all_found_configs = {config_path: config, base_path: base_config}

    mapping = MappingFile(
        config_path, config, all_found_configs, [os.path.abspath(".")]
    )

    assert mapping.path == config_path
    assert mapping.input_format == "foo"
    assert mapping.output_format == "bar"
    assert mapping.forward_transform == {"a": {"transformation": "b"}}
    assert mapping.reverse_transform == {"b": {"transformation": "a"}}
    assert all_found_configs[config_path] == mapping


def test_mapping_has_base___forward_transforms_are_merged():
    base_path = os.path.abspath("base.yml")
    base_config = {
        "input_format": "boo",
        "output_format": "bar",
        "forward_transform": {"c": {"transformation": "d"}},
        "reverse_transform": {"b": {"transformation": "d"}},
    }

    config_path = os.path.abspath("config.yml")
    config = {
        "bases": ["base"],
        "input_format": "foo",
        "forward_transform": {"a": {"transformation": "b"}},
        "reverse_transform": {"b": {"transformation": "a"}},
    }
    all_found_configs = {config_path: config, base_path: base_config}

    mapping = MappingFile(
        config_path, config, all_found_configs, [os.path.abspath(".")]
    )

    assert mapping.path == config_path
    assert mapping.input_format == "foo"
    assert mapping.output_format == "bar"
    assert mapping.forward_transform == {
        "a": {"transformation": "b"},
        "c": {"transformation": "d"},
    }
    assert mapping.reverse_transform == {"b": {"transformation": "a"}}
    assert all_found_configs[config_path] == mapping


def test_mapping_has_base___reverse_transforms_are_merged():
    base_path = os.path.abspath("base.yml")
    base_config = {
        "input_format": "boo",
        "output_format": "bar",
        "forward_transform": {"a": {"transformation": "d"}},
        "reverse_transform": {
            "b": {"transformation": "d"},
            "d": {"transformation": "c"},
        },
    }

    config_path = os.path.abspath("config.yml")
    config = {
        "bases": ["base"],
        "input_format": "foo",
        "forward_transform": {"a": {"transformation": "b"}},
        "reverse_transform": {"b": {"transformation": "a"}},
    }
    all_found_configs = {config_path: config, base_path: base_config}

    mapping = MappingFile(
        config_path, config, all_found_configs, [os.path.abspath(".")]
    )

    assert mapping.path == config_path
    assert mapping.input_format == "foo"
    assert mapping.output_format == "bar"
    assert mapping.forward_transform == {
        "a": {"transformation": "b"},
    }
    assert mapping.reverse_transform == {
        "b": {"transformation": "a"},
        "d": {"transformation": "c"},
    }
    assert all_found_configs[config_path] == mapping


@given(ext=sampled_from(["yml", "yaml"]))
def test_mapping_has_path_base___base_is_used(ext):
    base_path = os.path.abspath(f"base.{ext}")
    base_config = {
        "input_format": "foo",
        "output_format": "far",
        "forward_transform": {"a": {"transformation": "c"}},
        "reverse_transform": {"b": {"transformation": "d"}},
    }

    config_path = os.path.abspath("config.yml")
    config = {
        "bases": [f"base.{ext}"],
        "output_format": "bar",
        "forward_transform": {"a": {"transformation": "b"}},
        "reverse_transform": {"b": {"transformation": "a"}},
    }
    all_found_configs = {config_path: config, base_path: base_config}

    mapping = MappingFile(
        config_path, config, all_found_configs, [os.path.abspath(".")]
    )

    assert mapping.path == config_path
    assert mapping.input_format == "foo"
    assert mapping.output_format == "bar"
    assert mapping.forward_transform == {"a": {"transformation": "b"}}
    assert mapping.reverse_transform == {"b": {"transformation": "a"}}
    assert all_found_configs[config_path] == mapping


def test_mapping_has_multiple_base___later_bases_are_preferred():
    first_base_path = os.path.abspath("first.yml")
    first_base_config = {
        "input_format": "boo",
        "output_format": "bash",
        "forward_transform": {
            "a": {"transformation": "b"},
            "x": {"transformation": "y"},
        },
        "reverse_transform": {
            "b": {"transformation": "a"},
            "y": {"transformation": "x"},
        },
    }

    second_base_path = os.path.abspath("second.yaml")
    second_base_config = {
        "input_format": "fish",
        "output_format": "far",
        "forward_transform": {
            "c": {"transformation": "d"},
            "x": {"transformation": "z"},
        },
        "reverse_transform": {
            "d": {"transformation": "c"},
            "z": {"transformation": "x"},
        },
    }

    config_path = os.path.abspath("config.yml")
    config = {
        "bases": ["first", "second"],
        "input_format": "foo",
        "output_format": "bar",
        "forward_transform": {"e": {"transformation": "f"}},
        "reverse_transform": {"f": {"transformation": "e"}},
    }
    all_found_configs = {
        config_path: config,
        first_base_path: first_base_config,
        second_base_path: second_base_config,
    }

    mapping = MappingFile(
        config_path, config, all_found_configs, [os.path.abspath(".")]
    )

    assert mapping.path == config_path
    assert mapping.input_format == "foo"
    assert mapping.output_format == "bar"
    assert mapping.forward_transform == {
        "a": {"transformation": "b"},
        "c": {"transformation": "d"},
        "e": {"transformation": "f"},
        "x": {"transformation": "z"},
    }
    assert mapping.reverse_transform == {
        "b": {"transformation": "a"},
        "d": {"transformation": "c"},
        "f": {"transformation": "e"},
        "y": {"transformation": "x"},
        "z": {"transformation": "x"},
    }
    assert all_found_configs[config_path] == mapping


def test_mapping_has_base_with_base___grand_parent_bases_are_loaded():
    first_base_path = os.path.abspath("first.yml")
    first_base_config = {
        "input_format": "boo",
        "output_format": "bash",
        "forward_transform": {
            "a": {"transformation": "b"},
            "x": {"transformation": "y"},
        },
        "reverse_transform": {
            "b": {"transformation": "a"},
            "y": {"transformation": "x"},
        },
    }

    second_base_path = os.path.abspath("second.yaml")
    second_base_config = {
        "bases": ["first"],
        "output_format": "far",
        "forward_transform": {
            "c": {"transformation": "d"},
            "x": {"transformation": "z"},
        },
        "reverse_transform": {
            "d": {"transformation": "c"},
            "z": {"transformation": "x"},
        },
    }

    config_path = os.path.abspath("config.yml")
    config = {
        "bases": ["second"],
        "input_format": "foo",
        "output_format": "bar",
        "forward_transform": {"e": {"transformation": "f"}},
        "reverse_transform": {"f": {"transformation": "e"}},
    }
    all_found_configs = {
        config_path: config,
        first_base_path: first_base_config,
        second_base_path: second_base_config,
    }

    mapping = MappingFile(
        config_path, config, all_found_configs, [os.path.abspath(".")]
    )

    assert mapping.path == config_path
    assert mapping.input_format == "foo"
    assert mapping.output_format == "bar"
    assert mapping.forward_transform == {
        "a": {"transformation": "b"},
        "c": {"transformation": "d"},
        "e": {"transformation": "f"},
        "x": {"transformation": "z"},
    }
    assert mapping.reverse_transform == {
        "b": {"transformation": "a"},
        "d": {"transformation": "c"},
        "f": {"transformation": "e"},
        "y": {"transformation": "x"},
        "z": {"transformation": "x"},
    }
    assert all_found_configs[config_path] == mapping


def test_mapping_has_base_in_different_search_path___bases_is_loaded():
    other_search_path = "/somepath/"
    base_path = os.path.join(other_search_path, "base.yml")
    base_config = {
        "input_format": "boo",
        "output_format": "bar",
        "forward_transform": {"a": {"transformation": "d"}},
        "reverse_transform": {
            "b": {"transformation": "d"},
            "d": {"transformation": "c"},
        },
    }

    config_path = os.path.abspath("config.yml")
    config = {
        "bases": ["base"],
        "input_format": "foo",
        "forward_transform": {"a": {"transformation": "b"}},
        "reverse_transform": {"b": {"transformation": "a"}},
    }
    all_found_configs = {config_path: config, base_path: base_config}

    mapping = MappingFile(
        config_path,
        config,
        all_found_configs,
        [os.path.abspath("."), other_search_path],
    )

    assert mapping.path == config_path
    assert mapping.input_format == "foo"
    assert mapping.output_format == "bar"
    assert mapping.forward_transform == {
        "a": {"transformation": "b"},
    }
    assert mapping.reverse_transform == {
        "b": {"transformation": "a"},
        "d": {"transformation": "c"},
    }
    assert all_found_configs[config_path] == mapping


def test_mapping_file_has_forward_transform___can_run_forward_is_true():
    config_path = os.path.abspath("config.yml")
    config = {
        "input_format": "foo",
        "output_format": "bar",
        "forward_transform": {"a": {"transformation": "b"}},
        "reverse_transform": {"b": {"transformation": "a"}},
    }
    all_found_configs = {config_path: config}

    mapping = MappingFile(
        config_path, config, all_found_configs, [os.path.abspath(".")]
    )

    assert mapping.can_run_forwards is True


def test_mapping_file_has_no_forward_transform___can_run_forward_is_false():
    config_path = os.path.abspath("config.yml")
    config = {
        "input_format": "foo",
        "output_format": "bar",
        "reverse_transform": {"b": {"transformation": "a"}},
    }
    all_found_configs = {config_path: config}

    mapping = MappingFile(
        config_path, config, all_found_configs, [os.path.abspath(".")]
    )

    assert mapping.can_run_forwards is False


def test_mapping_file_has_reverse_transform___can_run_in_reverse_is_true():
    config_path = os.path.abspath("config.yml")
    config = {
        "input_format": "foo",
        "output_format": "bar",
        "forward_transform": {"a": {"transformation": "b"}},
        "reverse_transform": {"b": {"transformation": "a"}},
    }
    all_found_configs = {config_path: config}

    mapping = MappingFile(
        config_path, config, all_found_configs, [os.path.abspath(".")]
    )

    assert mapping.can_run_in_reverse is True


def test_mapping_file_has_no_reverse_transform___can_run_in_reverse_is_false():
    config_path = os.path.abspath("config.yml")
    config = {
        "input_format": "foo",
        "output_format": "bar",
        "forward_transform": {"a": {"transformation": "b"}},
    }
    all_found_configs = {config_path: config}

    mapping = MappingFile(
        config_path, config, all_found_configs, [os.path.abspath(".")]
    )

    assert mapping.can_run_in_reverse is False


#
# FileMapping tests
#


@given(paths=lists(text()))
def test_standard_and_current_path_is_added_to_the_abs_search_paths(paths):
    package_root_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..",)
    )

    assert FileMapping(search_paths=paths).search_paths == [
        os.path.abspath("."),
        *(os.path.abspath(p) for p in paths),
        os.path.join(package_root_dir, "converter", "_data", "mappings",),
    ]


def test_multiple_search_paths_contain_files___all_are_loaded():
    with TemporaryDirectory() as first, TemporaryDirectory() as second:
        write_yaml(
            os.path.join(first, "A-B.yml"),
            {"input_format": "A", "output_format": "B"},
        )
        write_yaml(
            os.path.join(first, "B-C.yaml"),
            {"input_format": "B", "output_format": "C"},
        )
        write_yaml(
            os.path.join(second, "C-D.yml"),
            {"input_format": "C", "output_format": "D"},
        )
        write_yaml(
            os.path.join(second, "D-E.yaml"),
            {"input_format": "D", "output_format": "E"},
        )

        mapping = FileMapping(
            search_paths=[first], standard_search_path=second,
        )

        loaded = mapping.mapping_configs

        assert loaded[os.path.join(first, "A-B.yml")].input_format == "A"
        assert loaded[os.path.join(first, "A-B.yml")].output_format == "B"

        assert loaded[os.path.join(first, "B-C.yaml")].input_format == "B"
        assert loaded[os.path.join(first, "B-C.yaml")].output_format == "C"

        assert loaded[os.path.join(second, "C-D.yml")].input_format == "C"
        assert loaded[os.path.join(second, "C-D.yml")].output_format == "D"

        assert loaded[os.path.join(second, "D-E.yaml")].input_format == "D"
        assert loaded[os.path.join(second, "D-E.yaml")].output_format == "E"


def test_yaml_files_with_non_mapping_fields_in_search_paths_are_excluded():
    with TemporaryDirectory() as first:
        write_yaml(
            os.path.join(first, "A-B.yml"),
            {"input_format": "A", "output_format": "B"},
        )
        write_yaml(
            os.path.join(first, "B-C.yaml"),
            {"input_format": "B", "output_format": "C"},
        )
        write_yaml(os.path.join(first, "other.yaml"), {"other_field": "foo"})

        mapping = FileMapping(standard_search_path=first)

        loaded = mapping.mapping_configs

        assert os.path.join(first, "A-B.yml") in loaded
        assert os.path.join(first, "B-C.yaml") in loaded
        assert os.path.join(first, "other.yaml") not in loaded


def test_invalid_mapping_exists___its_excluded_and_warning_is_written():
    with TemporaryDirectory() as first:
        write_yaml(
            os.path.join(first, "A-B.yml"),
            {"input_format": "A", "output_format": "B"},
        )
        write_yaml(
            os.path.join(first, "B-C.yaml"),
            {"input_format": "B", "output_format": "C"},
        )
        write_yaml(os.path.join(first, "invalid.yaml"), {"output_format": "D"})

        with patch("converter.mapping.file.logger") as logger_mock:
            mapping = FileMapping(standard_search_path=first)

            loaded = mapping.mapping_configs

            expected_error = InvalidMappingFile(
                "input_format not found in the config file or its bases",
                os.path.join(first, "invalid.yaml"),
            )

            logger_mock.warning.assert_called_once_with(str(expected_error))
            assert os.path.join(first, "A-B.yml") in loaded
            assert os.path.join(first, "B-C.yaml") in loaded
            assert os.path.join(first, "invalid.yaml") not in loaded
