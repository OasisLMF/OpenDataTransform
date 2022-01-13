import importlib
from typing import Any, Type
import threading

from ..config import Config
from ..config.config import TransformationConfig
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

    def run(self, threaded=True):
        """
        Generates the converter components from the config and runs the
        transformation
        """
        transformation_configs = self.config.get_transformation_configs()
        if threaded:
            threads = list(map(
                lambda c: threading.Thread(target=lambda: self._run_transformation(c)),
                transformation_configs
            ))

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()
        else:
            for c in transformation_configs:
                self._run_transformation(c)

    def _run_transformation(self, config: TransformationConfig):
        mapping_class: Type[BaseMapping] = self._load_from_module(
            config.get(
                "mapping.path", fallback="converter.mapping.FileMapping"
            )
        )
        mapping: BaseMapping = mapping_class(
            config,
            **config.get("mapping.options", fallback={}),
        )

        extractor_class: Type[BaseConnector] = self._load_from_module(
            config.get(
                "extractor.path", fallback="converter.connector.CsvConnector"
            )
        )
        extractor: BaseConnector = extractor_class(
            config, **config.get("extractor.options", fallback={})
        )

        loader_class: Type[BaseConnector] = self._load_from_module(
            config.get(
                "loader.path", fallback="converter.connector.CsvConnector"
            )
        )
        loader: BaseConnector = loader_class(
            config, **config.get("loader.options", fallback={})
        )

        runner_class: Type[BaseRunner] = self._load_from_module(
            config.get(
                "runner.path", fallback="converter.runner.PandasRunner"
            )
        )
        runner: BaseRunner = runner_class(
            config, **config.get("runner.options", fallback={})
        )

        runner.run(extractor, mapping, loader)
