from typing import Any, Dict, Iterable

from converter.config import Config
from converter.connector.base import BaseConnector
from converter.mapping.base import BaseMapping


class BaseRunner:
    """
    Runs the transformations on the extracted data and writes
    it to the data loader

    :param config: The global config for the system
    """

    def __init__(self, config: Config, **options):
        self.config = config
        self._options = options

    def run(
        self,
        extractor: BaseConnector,
        mapping: BaseMapping,
        loader: BaseConnector,
    ):
        """
        Runs the transformation process and swnds the data to the data loader

        :param extractor: The data connection to extract data from
        :param mapping: Mapping object describing the transformations to apply
        :param loader: The data connection to load data to
        """
        loader.load(self.transform(extractor, mapping))

    def transform(
        self, extractor: BaseConnector, mapping: BaseMapping
    ) -> Iterable[Dict[str, Any]]:
        """
        Performs the transformation

        :param extractor: The data connection to extract data from
        :param mapping: Mapping object describing the transformations to apply

        :return: An iterable containing the transformed data
        """
        raise NotImplementedError()
