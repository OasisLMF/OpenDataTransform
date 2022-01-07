import os
from tempfile import TemporaryDirectory

import pandas as pd
import yaml

from converter.validator.base import ValidationResult, ValidationResultEntry
from converter.validator.pandas import PandasValidator


def test_invalid_operator():
    val_config = {
        "entries": {
            "Invalid": {
                "operator": "invalid",
            }
        }
    }

    with TemporaryDirectory() as search_dir:
        validator = PandasValidator(search_paths=[search_dir])

        with open(os.path.join(search_dir, "validation_fmt.yaml"), "w") as f:
            yaml.dump(val_config, f)

        res = validator.run(
            pd.DataFrame(
                [
                    [1, 2],
                    [3, 4],
                    [5, 6],
                    [7, 8],
                ],
                columns=["a", "b"],
            ),
            "fmt",
        )

        assert res["validations"][0] == ValidationResult(
            name="Invalid",
            operator="invalid",
            entries=[ValidationResultEntry(error="Unknown operator")],
        )


def test_count():
    val_config = {
        "entries": {
            "Count": {
                "operator": "count",
            }
        }
    }

    with TemporaryDirectory() as search_dir:
        validator = PandasValidator(search_paths=[search_dir])

        with open(os.path.join(search_dir, "validation_fmt.yaml"), "w") as f:
            yaml.dump(val_config, f)

        res = validator.run(
            pd.DataFrame(
                [
                    [1, 2],
                    [3, 4],
                    [5, 6],
                    [7, 8],
                ],
                columns=["a", "b"],
            ),
            "fmt",
        )

        assert res["validations"][0] == ValidationResult(
            name="Count",
            operator="count",
            entries=[ValidationResultEntry(value="4")],
        )


def test_count_unique():
    val_config = {
        "entries": {
            "CountUnique": {
                "operator": "count-unique",
                "fields": ["a", "b"],
            }
        }
    }

    with TemporaryDirectory() as search_dir:
        validator = PandasValidator(search_paths=[search_dir])

        with open(os.path.join(search_dir, "validation_fmt.yaml"), "w") as f:
            yaml.dump(val_config, f)

        res = validator.run(
            pd.DataFrame(
                [
                    [1, 2],
                    [1, 9],
                    [3, 4],
                    [10, 4],
                    [5, 6],
                    [5, 11],
                    [7, 8],
                    [7, 12],
                ],
                columns=["a", "b"],
            ),
            "fmt",
        )

        assert res["validations"][0] == ValidationResult(
            name="CountUnique",
            operator="count-unique",
            entries=[
                ValidationResultEntry(value="5", field="a"),
                ValidationResultEntry(value="7", field="b"),
            ],
        )


def test_sum():
    val_config = {
        "entries": {
            "Sum": {
                "fields": ["a", "b"],
                "operator": "sum",
            }
        }
    }

    with TemporaryDirectory() as search_dir:
        validator = PandasValidator(search_paths=[search_dir])

        with open(os.path.join(search_dir, "validation_fmt.yaml"), "w") as f:
            yaml.dump(val_config, f)

        res = validator.run(
            pd.DataFrame(
                [
                    [1, 2],
                    [3, 4],
                    [5, 6],
                    [7, 8],
                ],
                columns=["a", "b"],
            ),
            "fmt",
        )

        assert res["validations"][0] == ValidationResult(
            name="Sum",
            operator="sum",
            entries=[
                ValidationResultEntry(field="a", value="16"),
                ValidationResultEntry(field="b", value="20"),
            ],
        )


def test_grouped_count():
    val_config = {
        "entries": {
            "GroupedCount": {
                "operator": "count",
                "group_by": ["g"],
            }
        }
    }

    with TemporaryDirectory() as search_dir:
        validator = PandasValidator(search_paths=[search_dir])

        with open(os.path.join(search_dir, "validation_fmt.yaml"), "w") as f:
            yaml.dump(val_config, f)

        res = validator.run(
            pd.DataFrame(
                [
                    [1, 1, 2],
                    [2, 3, 4],
                    [1, 5, 6],
                    [3, 7, 8],
                ],
                columns=["g", "a", "b"],
            ),
            "fmt",
        )

        assert res["validations"][0] == ValidationResult(
            name="GroupedCount",
            operator="count",
            entries=[
                ValidationResultEntry(value="2", groups={"g": "1"}),
                ValidationResultEntry(value="1", groups={"g": "2"}),
                ValidationResultEntry(value="1", groups={"g": "3"}),
            ],
        )


def test_multi_grouped_count():
    val_config = {
        "entries": {
            "MultiGroupedCount": {
                "operator": "count",
                "group_by": ["g1", "g2"],
            }
        }
    }

    with TemporaryDirectory() as search_dir:
        validator = PandasValidator(search_paths=[search_dir])

        with open(os.path.join(search_dir, "validation_fmt.yaml"), "w") as f:
            yaml.dump(val_config, f)

        res = validator.run(
            pd.DataFrame(
                [
                    [1, 1, 1, 2],
                    [2, 1, 3, 4],
                    [1, 2, 5, 6],
                    [3, 2, 7, 8],
                    [1, 1, 9, 10],
                    [1, 2, 11, 12],
                ],
                columns=["g1", "g2", "a", "b"],
            ),
            "fmt",
        )

        assert res["validations"][0] == ValidationResult(
            name="MultiGroupedCount",
            operator="count",
            entries=[
                ValidationResultEntry(
                    value="2", groups={"g1": "1", "g2": "1"}
                ),
                ValidationResultEntry(
                    value="2", groups={"g1": "1", "g2": "2"}
                ),
                ValidationResultEntry(
                    value="1", groups={"g1": "2", "g2": "1"}
                ),
                ValidationResultEntry(
                    value="1", groups={"g1": "3", "g2": "2"}
                ),
            ],
        )


def test_grouped_count_unique():
    val_config = {
        "entries": {
            "GroupedCountUnique": {
                "operator": "count-unique",
                "group_by": ["g"],
                "fields": ["a", "b"],
            }
        }
    }

    with TemporaryDirectory() as search_dir:
        validator = PandasValidator(search_paths=[search_dir])

        with open(os.path.join(search_dir, "validation_fmt.yaml"), "w") as f:
            yaml.dump(val_config, f)

        res = validator.run(
            pd.DataFrame(
                [
                    [1, 1, 2],
                    [1, 1, 9],
                    [2, 3, 4],
                    [2, 10, 4],
                    [1, 5, 6],
                    [3, 7, 8],
                ],
                columns=["g", "a", "b"],
            ),
            "fmt",
        )

        assert res["validations"][0] == ValidationResult(
            name="GroupedCountUnique",
            operator="count-unique",
            entries=[
                ValidationResultEntry(value="2", groups={"g": "1"}, field="a"),
                ValidationResultEntry(value="3", groups={"g": "1"}, field="b"),
                ValidationResultEntry(value="2", groups={"g": "2"}, field="a"),
                ValidationResultEntry(value="1", groups={"g": "2"}, field="b"),
                ValidationResultEntry(value="1", groups={"g": "3"}, field="a"),
                ValidationResultEntry(value="1", groups={"g": "3"}, field="b"),
            ],
        )


def test_multi_grouped_count_unique():
    val_config = {
        "entries": {
            "MultiGroupedCountUnique": {
                "operator": "count-unique",
                "group_by": ["g1", "g2"],
                "fields": ["a", "b"],
            }
        }
    }

    with TemporaryDirectory() as search_dir:
        validator = PandasValidator(search_paths=[search_dir])

        with open(os.path.join(search_dir, "validation_fmt.yaml"), "w") as f:
            yaml.dump(val_config, f)

        res = validator.run(
            pd.DataFrame(
                [
                    [1, 1, 1, 2],
                    [1, 1, 1, 13],
                    [2, 1, 3, 4],
                    [2, 1, 14, 4],
                    [1, 2, 5, 6],
                    [3, 2, 7, 8],
                    [1, 1, 9, 10],
                    [1, 2, 11, 12],
                    [1, 2, 15, 16],
                ],
                columns=["g1", "g2", "a", "b"],
            ),
            "fmt",
        )

        assert res["validations"][0] == ValidationResult(
            name="MultiGroupedCountUnique",
            operator="count-unique",
            entries=[
                ValidationResultEntry(
                    value="2",
                    groups={"g1": "1", "g2": "1"},
                    field="a",
                ),
                ValidationResultEntry(
                    value="3",
                    groups={"g1": "1", "g2": "1"},
                    field="b",
                ),
                ValidationResultEntry(
                    value="3",
                    groups={"g1": "1", "g2": "2"},
                    field="a",
                ),
                ValidationResultEntry(
                    value="3",
                    groups={"g1": "1", "g2": "2"},
                    field="b",
                ),
                ValidationResultEntry(
                    value="2",
                    groups={"g1": "2", "g2": "1"},
                    field="a",
                ),
                ValidationResultEntry(
                    value="1",
                    groups={"g1": "2", "g2": "1"},
                    field="b",
                ),
                ValidationResultEntry(
                    value="1",
                    groups={"g1": "3", "g2": "2"},
                    field="a",
                ),
                ValidationResultEntry(
                    value="1",
                    groups={"g1": "3", "g2": "2"},
                    field="b",
                ),
            ],
        )


def test_grouped_sum():
    val_config = {
        "entries": {
            "GroupedSum": {
                "fields": ["a", "b"],
                "operator": "sum",
                "group_by": ["g"],
            }
        }
    }

    with TemporaryDirectory() as search_dir:
        validator = PandasValidator(search_paths=[search_dir])

        with open(os.path.join(search_dir, "validation_fmt.yaml"), "w") as f:
            yaml.dump(val_config, f)

        res = validator.run(
            pd.DataFrame(
                [
                    [1, 1, 2],
                    [2, 3, 4],
                    [1, 5, 6],
                    [3, 7, 8],
                ],
                columns=["g", "a", "b"],
            ),
            "fmt",
        )

        assert res["validations"][0] == ValidationResult(
            name="GroupedSum",
            operator="sum",
            entries=[
                ValidationResultEntry(value="6", groups={"g": "1"}, field="a"),
                ValidationResultEntry(value="8", groups={"g": "1"}, field="b"),
                ValidationResultEntry(value="3", groups={"g": "2"}, field="a"),
                ValidationResultEntry(value="4", groups={"g": "2"}, field="b"),
                ValidationResultEntry(value="7", groups={"g": "3"}, field="a"),
                ValidationResultEntry(value="8", groups={"g": "3"}, field="b"),
            ],
        )


def test_multi_grouped_sum():
    val_config = {
        "entries": {
            "MultiGroupedSum": {
                "fields": ["a", "b"],
                "operator": "sum",
                "group_by": ["g1", "g2"],
            }
        }
    }

    with TemporaryDirectory() as search_dir:
        validator = PandasValidator(search_paths=[search_dir])

        with open(os.path.join(search_dir, "validation_fmt.yaml"), "w") as f:
            yaml.dump(val_config, f)

        res = validator.run(
            pd.DataFrame(
                [
                    [1, 1, 1, 2],
                    [2, 1, 3, 4],
                    [1, 2, 5, 6],
                    [3, 2, 7, 8],
                    [1, 1, 9, 10],
                    [1, 2, 11, 12],
                ],
                columns=["g1", "g2", "a", "b"],
            ),
            "fmt",
        )

        assert res["validations"][0] == ValidationResult(
            name="MultiGroupedSum",
            operator="sum",
            entries=[
                ValidationResultEntry(
                    value="10", groups={"g1": "1", "g2": "1"}, field="a"
                ),
                ValidationResultEntry(
                    value="12", groups={"g1": "1", "g2": "1"}, field="b"
                ),
                ValidationResultEntry(
                    value="16", groups={"g1": "1", "g2": "2"}, field="a"
                ),
                ValidationResultEntry(
                    value="18", groups={"g1": "1", "g2": "2"}, field="b"
                ),
                ValidationResultEntry(
                    value="3", groups={"g1": "2", "g2": "1"}, field="a"
                ),
                ValidationResultEntry(
                    value="4", groups={"g1": "2", "g2": "1"}, field="b"
                ),
                ValidationResultEntry(
                    value="7", groups={"g1": "3", "g2": "2"}, field="a"
                ),
                ValidationResultEntry(
                    value="8", groups={"g1": "3", "g2": "2"}, field="b"
                ),
            ],
        )
