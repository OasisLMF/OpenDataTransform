import os

import pytest
from hypothesis import given
from hypothesis.strategies import sampled_from

from converter.mapping.file import InvalidMappingFile, MappingFile


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
