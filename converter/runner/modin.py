import os

from .pandas import PandasRunner


class ModinRunner(PandasRunner):
    def __init__(self, **options):
        super().__init__(**options)
        self.engine = options.get("engine", "dask")

    def get_dataframe(self, extractor):
        os.environ.setdefault("MODIN_ENGINE", self.engine)
        import modin.pandas as pd  # must be imported after modin engine is set

        return pd.DataFrame(extractor.extract())
