from converter.errors import ConverterError


class DBConnectionError(ConverterError):
    pass


class DBQueryError(ConverterError):
    def __init__(self, query, error, data=None):
        self.query = query
        self.data = data
        self.error = error

        super().__init__(
            f"Error running query: {query} with {data} - {error}"
        )


class DBInsertDataError(ConverterError):
    pass
