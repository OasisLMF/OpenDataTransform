import csv
import os
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pytest

from converter.config import Config
from converter.connector import CsvConnector


def test_file_does_not_exist___error_is_raised():
    connector = CsvConnector(Config(), path="somepath.csv")

    with pytest.raises(FileNotFoundError):
        list(connector.extract())


def test_file_contains_data_with_heading___all_entries_are_loaded():
    expected_data = [
        {"a": 1, "b": 2},
        {"a": 3, "b": 4},
        {"a": 5, "b": 6},
    ]

    with NamedTemporaryFile("w+", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["a", "b"], quoting=csv.QUOTE_NONNUMERIC
        )
        writer.writeheader()
        writer.writerows(expected_data)
        f.flush()

        assert (
            list(CsvConnector(Config(), path=f.name).extract())
            == expected_data
        )


def test_no_data_is_passed_to_loader___no_file_is_written():
    with TemporaryDirectory() as p:
        output_path = os.path.join(p, "result.csv")

        CsvConnector(Config(), path=output_path).load([])

        assert not os.path.exists(output_path)


def test_data_is_passed_to_loader___data_with_heading_is_written_to_file():
    expected_data = [
        {"a": 1, "b": 2},
        {"a": 3, "b": 4},
        {"a": 5, "b": 6},
    ]

    with TemporaryDirectory() as p:
        output_path = os.path.join(p, "result.csv")

        CsvConnector(Config(), path=output_path).load(expected_data)

        with open(output_path, "r") as f:
            assert (
                list(csv.DictReader(f, quoting=csv.QUOTE_NONNUMERIC))
                == expected_data
            )


def test_data_is_passed_to_loader_no_header___data_is_written_to_file():
    expected_data = [
        {"a": 1, "b": 2},
        {"a": 3, "b": 4},
        {"a": 5, "b": 6},
    ]

    with TemporaryDirectory() as p:
        output_path = os.path.join(p, "result.csv")

        CsvConnector(
            Config(),
            path=output_path,
            write_header=False,
        ).load(expected_data)

        with open(output_path, "r") as f:
            assert (
                list(
                    csv.DictReader(
                        f,
                        quoting=csv.QUOTE_NONNUMERIC,
                        fieldnames=["a", "b"],
                    )
                )
                == expected_data
            )
