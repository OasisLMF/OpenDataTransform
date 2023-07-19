import os

from ..files.csv import BufferedCsvReader
from ..types.notset import NotSetType
from .pandas import PandasRunner


class ModinRunner(PandasRunner):
    name = "Modin"
    options_schema = {
        "type": "object",
        "properties": {
            "engine": {
                "type": "string",
                "enum": ["dask", "ray"],
                "default": "dask",
                "title": "Engine",
            }
        },
    }

    def __init__(self, config, **options):
        super().__init__(config, **options)
        self.engine = options.get("engine", "dask")

    def get_dataframe(self, extractor):
        os.environ.setdefault("MODIN_ENGINE", self.engine)
        import modin.pandas as pd  # must be imported after modin engine is set

        extracted = extractor.extract()

        # the extractor may return a pandas dataframe,
        # in this case return this rather than creating a
        # new dataframe object
        if isinstance(extracted, pd.DataFrame):
            return extracted

        self.dataframe_type = pd.DataFrame
        self.series_type = pd.Series
        return pd.read_csv(BufferedCsvReader(extracted))

    def combine_column(self, *args, **kwargs):
        combined = super().combine_column(*args, **kwargs)
        if not isinstance(combined, NotSetType) and "__reduced__" in combined:
            return combined["__reduced__"]
        else:
            return combined
