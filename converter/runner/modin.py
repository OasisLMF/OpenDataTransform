import csv
import os

from ..files.csv import BufferedCsvReader
from .base import NotSetType
from .pandas import PandasRunner


class ModinRunner(PandasRunner):
    def __init__(self, config, **options):
        super().__init__(config, **options)
        self.engine = options.get("engine", "dask")

    def get_dataframe(self, extractor):
        os.environ.setdefault("MODIN_ENGINE", self.engine)
        import modin.pandas as pd  # must be imported after modin engine is set

        self.dataframe_type = pd.DataFrame
        self.series_type = pd.Series
        return pd.read_csv(
            BufferedCsvReader(extractor.extract()),
            quoting=csv.QUOTE_NONNUMERIC,
        )

    def combine_column(self, *args, **kwargs):
        combined = super().combine_column(*args, **kwargs)
        if not isinstance(combined, NotSetType) and "__reduced__" in combined:
            return combined["__reduced__"]
        else:
            return combined
