import logging
import os
from functools import reduce
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    TypedDict,
    TypeVar,
    Union,
)

import yaml

from converter.config.config import TransformationConfig
from converter.data import get_data_path
from converter.files.yaml import read_yaml

DataType = TypeVar("DataType")
GroupedDataType = TypeVar("GroupedDataType")
GroupedDataType_cov = TypeVar("GroupedDataType_cov", covariant=True)


def get_logger():
    return logging.getLogger(__name__)


class ValidationResultEntry(TypedDict, total=False):
    field: Optional[str]
    groups: Optional[Dict[str, Any]]
    value: Optional[Any]
    error: Optional[str]


class ValidationResult(TypedDict):
    name: str
    operator: str
    entries: List[ValidationResultEntry]


class ValidationLogEntry(TypedDict):
    file_type: str
    format: str
    validation_file: Optional[str]
    validations: List[ValidationResult]


class ValidatorConfigEntry:
    def __init__(self, validator_name, config):
        self.validator_name = validator_name
        self.fields = config.get("fields", [])
        self.operator = config.get("operator", "sum")
        self.group_by = config.get("group_by", None)

    def __eq__(self, other):
        return all(
            [
                self.validator_name == other.validator_name,
                self.fields == other.fields,
                self.operator == other.operator,
                self.group_by == other.group_by,
            ]
        )


class ValidatorConfig:
    def __init__(self, path=None, raw_config=None):
        if raw_config:
            self.raw_config = raw_config
        else:
            self.path = path
            self.raw_config = read_yaml(self.path)

        self.entries = [
            ValidatorConfigEntry(k, v)
            for k, v in self.raw_config.get("entries", {}).items()
        ]

    def __eq__(self, other):
        return self.entries == other.entries


class BaseValidator(Generic[DataType, GroupedDataType]):
    def __init__(
        self,
        search_paths: List[str] = None,
        standard_search_path: str = get_data_path("validators"),
        search_working_dir=True,
        config: TransformationConfig = None,
    ):
        self.config = config
        self.search_paths = [
            *(search_paths or []),
            *([os.getcwd()] if search_working_dir else []),
            standard_search_path,
        ]

    def load_config(
        self, fmt, version, file_type
    ) -> Union[None, ValidatorConfig]:
        if self.config and self.config.get(f'mapping.validation.{fmt}', None):
            # if there is a validation entry in the config use that for the validation config
            config_path = self.config.get(f'mapping.validation.{fmt}')
        else:
            # Build the candidate paths with and without the version preferring
            # with the version if its available
            candidate_paths = [
                os.path.join(p, f"validation_{fmt}_v{version}_{file_type}.yaml")
                for p in self.search_paths
            ] + [
                os.path.join(p, f"validation_{fmt}_{file_type}.yaml")
                for p in self.search_paths
            ]

            # find the first validation config path that matches the format
            config_path = reduce(
                lambda found, current: found
                or (current if os.path.exists(current) else None),
                candidate_paths,
                None,
            )

            if not config_path:
                get_logger().warning(
                    f"Could not find validator config for {fmt}. "
                    f"Tried paths {', '.join(candidate_paths)}"
                )
                return None

        return ValidatorConfig(config_path)

    def run(self, data: DataType, fmt: str, version: str, file_type: str):
        config = self.load_config(fmt, version, file_type)

        result: ValidationLogEntry = {
            "file_type": file_type,
            "format": fmt,
            "validation_file": config.path if config else None,
            "validations": [],
        }
        if config:
            for entry in config.entries:
                result["validations"].append(self.run_entry(data, entry))

        get_logger().info(yaml.safe_dump([result]))
        return result

    def group_data(
        self, data: DataType, group_by: List[str], entry: ValidatorConfigEntry
    ) -> GroupedDataType_cov:  # pragma: no cover
        raise NotImplementedError()

    def sum(
        self,
        data: Union[DataType, GroupedDataType],
        entry: ValidatorConfigEntry,
    ) -> List[ValidationResultEntry]:  # pragma: no cover
        raise NotImplementedError()

    def count(
        self,
        data: Union[DataType, GroupedDataType],
        entry: ValidatorConfigEntry,
    ) -> List[ValidationResultEntry]:  # pragma: no cover
        raise NotImplementedError()

    def count_unique(
        self,
        data: Union[DataType, GroupedDataType],
        entry: ValidatorConfigEntry,
    ) -> List[ValidationResultEntry]:  # pragma: no cover
        raise NotImplementedError()

    def run_entry(
        self, data: DataType, entry: ValidatorConfigEntry
    ) -> ValidationResult:
        if entry.group_by is not None:
            data = self.group_data(data, entry.group_by, entry)

        if entry.operator == "sum":
            return ValidationResult(
                name=entry.validator_name,
                operator=entry.operator,
                entries=self.sum(data, entry),  # types: ignore
            )
        elif entry.operator == "count":
            return ValidationResult(
                name=entry.validator_name,
                operator=entry.operator,
                entries=self.count(data, entry),  # types: ignore
            )
        elif entry.operator == "count-unique":
            return ValidationResult(
                name=entry.validator_name,
                operator=entry.operator,
                entries=self.count_unique(data, entry),  # types: ignore
            )
        else:
            return ValidationResult(
                name=entry.validator_name,
                operator=entry.operator,
                entries=[{"error": "Unknown operator"}],
            )
