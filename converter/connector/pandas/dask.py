import dask.dataframe as dd
from lot3.filestore.filestore import parse_url_options

from converter.connector.pandas.pandas import PandasConnector


class DaskConnector(PandasConnector):
    def load_csv(self, data: dd.DataFrame):
        _, path, opts = parse_url_options(self.file_path)
        data.to_csv(path, **opts)

    def load_parquet(self, data: dd.DataFrame):
        _, path, opts = parse_url_options(self.file_path)
        data.to_parquet(path, **opts)

    def extract_csv(self):
        _, path, opts = parse_url_options(self.file_path)
        return dd.read_csv(path, **opts)

    def extract_parquet(self):
        _, path, opts = parse_url_options(self.file_path)
        return dd.read_parquet(path, **opts)
