import os

from ..files.csv import BufferedCsvReader
from .pandas import PandasRunner


class ModinRunner(PandasRunner):
    def __init__(self, config, **options):
        super().__init__(config, **options)
        self.engine = options.get("engine", "dask")

    def combine_series(self, first, second):
        """
        Helper function for combining 2 series.

        Modin doesnt quite follow the same behaviour as pandas and stored the
        combined column in a data frame column called `__reduce__` if `first`
        has data so we take this column if present as the result.

        :param first: The preferred series to take data from
        :param second: The secondary series to take data from

        :return: The combined series
        """
        res = super().combine_series(first, second)
        return getattr(res, "__reduced__", res)

    def get_dataframe(self, extractor):
        os.environ.setdefault("MODIN_ENGINE", self.engine)
        import modin.pandas as pd  # must be imported after modin engine is set

        self.dataframe_type = pd.DataFrame
        self.series_type = pd.Series
        return pd.read_csv(BufferedCsvReader(extractor.extract()))
