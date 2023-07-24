import dask.dataframe as dd

from converter.connector.pandas.pandas import PandasConnector


class DaskConnector(PandasConnector):
    def load_csv(self, data: dd.DataFrame):
        data.to_csv(self.file_path)

    def load_parquet(self, data: dd.DataFrame):
        data.to_parquet(self.file_path)

    def extract_csv(self):
        return dd.read_csv(self.file_path)

    def extract_parquet(self):
        return dd.read_parquet(self.file_path)
