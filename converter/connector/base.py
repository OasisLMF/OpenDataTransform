from typing import Any, AsyncIterable, Dict, Iterable

from converter.config.config import TransformationConfig


class BaseConnector:
    """
    Connects to the the data source

    :param config: The global config for the system
    :param options_schema: A dictionary representing the
        schema of field connectors options json schema property
        types (https://python-jsonschema.readthedocs.io/en/stable/)
    :param name: The human readable name of the connector for
        use in the UI
    """

    name = "Base Connector"
    options_schema = {"type": "object", "properties": {}}

    def __init__(self, config: TransformationConfig, **options):
        self._options = options
        self.config = config

    def extract(self) -> Iterable[Dict[str, Any]]:
        """
        Extracts the data from the connected source and returns
        an iterable of dictionaries.

        :return: An iterable of the extracted data
        """
        raise NotImplementedError()

    async def aextract(self) -> AsyncIterable[Dict[str, Any]]:
        """
        Extracts the data from the connected source and returns
        an asynchronous iterable of dictionaries.

        :return: An iterable of the extracted data
        """
        raise NotImplementedError()
        yield {}  # pragma: no cover

    def load(self, data: Iterable[Dict[str, Any]]):
        """
        Loads the data into the connected data object.

        :param data: An iterable of dictionaries representing
            the data to push to the connected source.
        """
        raise NotImplementedError()

    async def aload(self, data: AsyncIterable[Dict[str, Any]]):
        """
        Loads the data into the connected data object.

        :param data: An iterable of dictionaries representing
            the data to push to the connected source.
        """
        raise NotImplementedError()

    @classmethod
    def fully_qualified_name(cls):
        return f"{cls.__module__}.{cls.__qualname__}"
