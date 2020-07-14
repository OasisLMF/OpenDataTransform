import importlib
from typing import Any, Type

from ..config import Config
from ..connector.base import BaseConnector
from ..mapping.base import BaseMapping
from ..runner.base import BaseRunner


class Controller:
    """
    Class controlling the transformation flow

    :param config: The resolved normalised config
    """

    def __init__(self, config: Config):
        self.config = config

    def _load_from_module(self, path: str) -> Any:
        module_path, cls = path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        return getattr(module, cls)

    def run(self):
        """
        Generates the converter components from the config and runs the
        transformation
        """
        mapping_class: Type[BaseMapping] = self._load_from_module(
            self.config.get(
                "mapping.path", fallback="converter.mapping.FileMapping"
            )
        )
        mapping: BaseMapping = mapping_class(
            self.config, **self.config.get("mapping.options", fallback={})
        )

        extractor_class: Type[BaseConnector] = self._load_from_module(
            self.config.get(
                "extractor.path", fallback="converter.connector.CsvConnector"
            )
        )
        extractor: BaseConnector = extractor_class(
            self.config, **self.config.get("extractor.options", fallback={})
        )

        loader_class: Type[BaseConnector] = self._load_from_module(
            self.config.get(
                "loader.path", fallback="converter.connector.CsvConnector"
            )
        )
        loader: BaseConnector = loader_class(
            self.config, **self.config.get("loader.options", fallback={})
        )

        runner_class: Type[BaseRunner] = self._load_from_module(
            self.config.get(
                "runner.path", fallback="converter.runner.ModinRunner"
            )
        )
        runner: BaseRunner = runner_class(
            self.config, **self.config.get("runner.options", fallback={})
        )

        runner.run(extractor, mapping, loader)
