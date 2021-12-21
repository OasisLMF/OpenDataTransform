import logging
import os
from functools import reduce

import yaml
from typing import Union, List, TypeVar, Tuple, Any, Optional

from converter.data import get_data_path


DataType = TypeVar("DataType")
GroupedDataType = TypeVar("GroupedDataType")
ValidationResult = Tuple[str, Union[str, int, float]]


def get_logger():
    return logging.getLogger(__name__)


class ValidatorConfigEntry:
    def __init__(self, validator_name, config):
        self.validator_name = validator_name
        self.fields = config.get("fields", [])
        self.operator = config.get("operator", "sum")
        self.group_by = config.get("group_by", None)


class ValidatorConfig:
    def __init__(self, path):
        self.path = path

        with open(self.path) as f:
            self.raw_config = yaml.load(f, yaml.Loader)
            self.entries = [ValidatorConfigEntry(k, v) for k, v in self.raw_config.get("entries", []).items()]


class BaseValidator:
    def __init__(
        self,
        mapping,
        search_paths: List[str] = None,
        standard_search_path: str = get_data_path("validators"),
        search_working_dir=True,
    ):
        self.mapping = mapping
        self.search_paths = [
            *(search_paths or []),
            *([os.getcwd()] if search_working_dir else []),
            standard_search_path,
        ]

    def load_config(self, fmt) -> Union[None, ValidatorConfig]:
        candidate_paths = [
            os.path.join(p, f"validation_{fmt}.yaml") for p in self.search_paths
        ]

        # find the first validation config path that matches the format
        config_path = reduce(
            lambda found, current: found or (current if os.path.exists(current) else None),
            candidate_paths,
            None
        )

        if not config_path:
            get_logger().warning(f"Could not find validator config for {fmt}. Tried paths {', '.join(candidate_paths)}")
            return None

        return ValidatorConfig(config_path)

    def run(self, data: DataType, fmt: str):
        config = self.load_config(fmt)

        get_logger().info(f"Validation for {fmt}")
        for entry in config.entries:
            for result in self.run_entry(data, entry):
                get_logger().info(f"{result[0]}: {result[1]}")

    def group_data(self, data: DataType, group_by: List[str], entry: ValidatorConfigEntry) -> GroupedDataType:
        raise NotImplementedError()

    def sum(self, data: Union[DataType, GroupedDataType], entry: ValidatorConfigEntry) -> List[ValidationResult]:
        raise NotImplementedError()

    def count(self, data: Union[DataType, GroupedDataType], entry: ValidatorConfigEntry) -> List[ValidationResult]:
        raise NotImplementedError()

    def run_entry(self, data: DataType, entry: ValidatorConfigEntry) -> List[ValidationResult]:
        if entry.group_by is not None:
            data = self.group_data(data, entry.group_by, entry)

        if entry.operator == "sum":
            return self.sum(data, entry)
        elif entry.operator == "count":
            return self.count(data, entry)
        else:
            return [(entry.validator_name, "Unknown operator")]

    def generate_result_name(self, entry: ValidatorConfigEntry, field_name=None, index_values: Optional[List[Any]] = None):
        fmt_index = "" if index_values is None else f"({', '.join(map(str, index_values))})"
        fmt_field_name = "" if field_name is None else f" - {field_name}"
        return f"{entry.validator_name}{fmt_index}{fmt_field_name}"
