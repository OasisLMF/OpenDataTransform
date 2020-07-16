from itertools import chain, islice

import dask
import pandas as pd
from dask import dataframe as dd

from .pandas import PandasRunner


@dask.delayed
def read_pandas_chunk(c):
    # pragma: no cover
    # This is not picked up by coverage since it's a delayed dask object
    return pd.DataFrame(c)


class DaskRunner(PandasRunner):
    dataframe_type = dd.DataFrame
    series_type = dd.Series

    def __init__(self, config, **options):
        super().__init__(config, **options)

        self.chunk_size = int(options.get("chunk_size", 10000))

    def create_series(self, index, value):
        return index.to_series().apply(lambda x: value)

    def chunk(self, iterable):
        iterable = iter(iterable)
        while True:
            try:
                slice = islice(iterable, self.chunk_size)
                first_elem = next(slice)
                yield chain((first_elem,), slice)
            except StopIteration:
                return

    def get_dataframe(self, extractor):
        return dd.from_delayed(
            [read_pandas_chunk(c) for c in self.chunk(extractor.extract())]
        )
