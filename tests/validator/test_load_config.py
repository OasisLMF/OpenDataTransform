import os
from tempfile import TemporaryDirectory
from typing import Type
from unittest.mock import Mock, patch

import yaml
from hypothesis import given

from converter.validator.base import BaseValidator, ValidatorConfig
from tests.helpers import change_cwd
from tests.validator.strategies import validator_classes


@given(
    validator_class=validator_classes(),
)
def test_config_does_not_exist___warning_is_raised(
    validator_class: Type[BaseValidator],
):
    validator = validator_class()

    log_mock = Mock()
    with patch("converter.validator.base.get_logger", return_value=log_mock):
        validator.load_config("missing_format")

        candidate_paths = map(
            lambda s: os.path.join(s, "validation_missing_format.yaml"),
            validator.search_paths,
        )

        log_mock.warning.assert_called_once_with(
            f"Could not find validator config "
            f"for missing_format. Tried paths {', '.join(candidate_paths)}"
        )


@given(
    validator_class=validator_classes(),
)
def test_config_exists_in_standard_dir___standard_file_is_used(
    validator_class: Type[BaseValidator],
):
    std_val_config = {"entries": {"StdTest": {"operator": "count"}}}

    with TemporaryDirectory() as std_dir:
        validator = validator_class(standard_search_path=std_dir)

        with open(
            os.path.join(std_dir, "validation_test_format.yaml"), "w"
        ) as f:
            yaml.dump(std_val_config, f)

        assert validator.load_config("test_format") == ValidatorConfig(
            raw_config=std_val_config
        )


@given(
    validator_class=validator_classes(),
)
def test_config_exists_in_working_dir___working_dir_file_is_used(
    validator_class: Type[BaseValidator],
):
    std_val_config = {"entries": {"StdTest": {"operator": "count"}}}
    cwd_val_config = {"entries": {"CwdTest": {"operator": "count"}}}

    with (
        TemporaryDirectory() as std_dir,
        TemporaryDirectory() as cw_dir,
        change_cwd(cw_dir),
    ):
        validator = validator_class(
            standard_search_path=std_dir,
        )

        with open(
            os.path.join(std_dir, "validation_test_format.yaml"), "w"
        ) as f:
            yaml.dump(std_val_config, f)

        with open(
            os.path.join(cw_dir, "validation_test_format.yaml"), "w"
        ) as f:
            yaml.dump(cwd_val_config, f)

        assert validator.load_config("test_format") == ValidatorConfig(
            raw_config=cwd_val_config
        )


@given(
    validator_class=validator_classes(),
)
def test_config_exists_in_search_dir___search_dir_file_is_used(
    validator_class: Type[BaseValidator],
):
    std_val_config = {"entries": {"StdTest": {"operator": "count"}}}
    cwd_val_config = {"entries": {"CwdTest": {"operator": "count"}}}
    search_dir_val_config = {
        "entries": {"SearchDirTest": {"operator": "count"}}
    }

    with (
        TemporaryDirectory() as std_dir,
        TemporaryDirectory() as cw_dir,
        TemporaryDirectory() as search_dir,
        change_cwd(cw_dir),
    ):
        validator = validator_class(
            standard_search_path=std_dir,
            search_paths=[search_dir],
        )

        with open(
            os.path.join(std_dir, "validation_test_format.yaml"), "w"
        ) as f:
            yaml.dump(std_val_config, f)

        with open(
            os.path.join(cw_dir, "validation_test_format.yaml"), "w"
        ) as f:
            yaml.dump(cwd_val_config, f)

        with open(
            os.path.join(search_dir, "validation_test_format.yaml"), "w"
        ) as f:
            yaml.dump(search_dir_val_config, f)

        assert validator.load_config("test_format") == ValidatorConfig(
            raw_config=search_dir_val_config
        )
