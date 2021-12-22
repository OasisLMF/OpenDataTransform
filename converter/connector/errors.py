from converter.errors import ConverterError


class SQLiteConnectionError(ConverterError):
    pass


class SQLiteQueryError(ConverterError):
    def __init__(self, query, data=None):
        self.query = query
        self.data = data

        super().__init__(
            f"Error running query: {query} with {data}."
        )


class SQLiteInsertDataError(ConverterError):
    pass
