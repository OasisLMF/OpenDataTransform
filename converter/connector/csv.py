import csv
from typing import Any, Dict, Iterable

from converter.connector.base import BaseConnector
from converter.types.notset import NotSetType


class CsvConnector(BaseConnector):
    """
    Connects to a csv file on the local machine for reading and writing data.

    **Options:**

    * `path` - The path to the csv file to read/write
    * `write_header` - Flag whether the header row should be written to the
      target when loading data (default: `True`)
    * `quoting` - What type of quoting should be used when reading and writing
      data. Valid values are `all`, `minimal`, `nonnumeric` and `none`.
      Descriptions of these values are given in the
      `python csv module documentation
      <https://docs.python.org/3/library/csv.html#csv.QUOTE_ALL>`__.
      (default: `nonnumeric`).
    """

    name = "CSV Connector"
    options_schema = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The path to the file to load relative to the config file",
            },
            "write_header": {
                "type": "boolean",
                "description": "Should the header row be written?",
                "default": True
            },
            "quoting": {
                "type": "string",
                "description": "The type of quoting to use when reading/writing entries (see https://docs.python.org/3/library/csv.html#csv.QUOTE_ALL for a description of the values)",
                "enum": ["all", "minimal", "none", "nonnumeric"]
            }
        },
        "required": ["path"],
    }

    def __init__(self, config, **options):
        super().__init__(config, **options)

        self.file_path = config.absolute_path(options["path"])
        self.write_header = options.get("write_header", True)
        self.quoting = {
            "all": csv.QUOTE_ALL,
            "minimal": csv.QUOTE_MINIMAL,
            "none": csv.QUOTE_NONE,
            "nonnumeric": csv.QUOTE_NONNUMERIC,
        }.get(options.get("quoting", "nonnumeric"))

    def _data_serializer(self, row):
        return {
            k: v if v is not None and not isinstance(v, NotSetType) else ""
            for k, v in row.items()
        }

    def load(self, data: Iterable[Dict[str, Any]]):
        try:
            data = iter(data)
            first_row = next(data)
        except StopIteration:
            return

        with open(self.file_path, "w", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=list(first_row.keys()), quoting=self.quoting
            )

            if self.write_header:
                writer.writeheader()

            writer.writerow(self._data_serializer(first_row))
            writer.writerows(map(self._data_serializer, data))

    def extract(self) -> Iterable[Dict[str, Any]]:
        with open(self.file_path, "r") as f:
            yield from csv.DictReader(f, quoting=self.quoting)
