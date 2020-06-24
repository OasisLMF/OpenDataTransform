import csv
from typing import Any, Dict, Iterable

from converter.connector.base import BaseConnector


class CsvConnector(BaseConnector):
    def __init__(self, **options):
        super().__init__(**options)

        self.file_path = options["path"]
        self.write_header = options.get("write_header", True)
        self.quoting = {
            "all": csv.QUOTE_ALL,
            "minimal": csv.QUOTE_MINIMAL,
            "none": csv.QUOTE_NONE,
            "nonnumeric": csv.QUOTE_NONNUMERIC,
        }.get(options.get("quoting", "nonnumeric"))

    def load(self, data: Iterable[Dict[str, Any]]):
        try:
            data = iter(data)
            first_row = next(data)
        except StopIteration:
            return

        with open(self.file_path, "w", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=first_row.keys(), quoting=self.quoting
            )

            if self.write_header:
                writer.writeheader()

            writer.writerow(first_row)
            writer.writerows(data)

    def extract(self) -> Iterable[Dict[str, Any]]:
        with open(self.file_path, "r") as f:
            yield from csv.DictReader(f, quoting=self.quoting)
