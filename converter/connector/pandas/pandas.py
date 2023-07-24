from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable

import pandas as pd

from converter.config.errors import ConfigurationError
from converter.connector import BaseConnector


class PandasFileTypes(Enum):
    csv = "csv"
    parquet = "parquet"


class PandasConnector(BaseConnector):
    def __init__(self, config, **options):
        self.file_path = config.absolute_path(options["path"])

        if "file_type" in options:
            self.file_type = config.absolute_path(options.get("file_type"))
        else:
            ext = Path(self.file_path).suffix
            self.file_type = {
                "csv": PandasFileTypes.csv,
                "parquet": PandasFileTypes.parquet,
                "pq": PandasFileTypes.parquet,
            }.get(ext)

            if not self.file_type:
                raise ConfigurationError(
                    f"File type was not recognised from the extension {ext} and 'file_type' options was not provided"
                )

        super().__init__(config, **options)

    def load_csv(self, data: pd.DataFrame):
        data.to_csv(self.file_path)

    def load_parquet(self, data: pd.DataFrame):
        data.to_parquet(self.file_path)

    def load(self, data: pd.DataFrame):
        if self.file_type == PandasFileTypes.csv:
            return self.load_csv(data)
        elif self.file_type == PandasFileTypes.parquet:
            return self.load_parquet(data)

    def extract_csv(self):
        return pd.read_csv(self.file_path)

    def extract_parquet(self):
        return pd.read_parquet(self.file_path)

    def extract(self) -> Iterable[Dict[str, Any]]:
        if self.file_type == PandasFileTypes.csv:
            return self.extract_csv()
        elif self.file_type == PandasFileTypes.parquet:
            return self.extract_parquet()
