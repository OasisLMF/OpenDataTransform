import importlib
import logging
import sys
import threading
import traceback
from datetime import datetime
from typing import Any, Type

from ..config import Config
from ..config.config import TransformationConfig
from ..connector.base import BaseConnector
from ..mapping.base import BaseMapping
from ..runner.base import BaseRunner


def get_logger():
    return logging.getLogger(__name__)


class Controller:
    """
    Class controlling the transformation flow

    :param config: The resolved normalised config
    :param raise_errors: If true, errors during the conversion process
        will be raises, if not they will only be logged
    :param logger: A python logger object. If supplied, it will override
        the standard logger.
    """

    def __init__(self, config: Config, raise_errors=False, logger=None, redact_logs=False):
        self.config = config
        self.raise_errors = raise_errors
        self.logger = logger
        self.redact_logs = redact_logs

    def get_logger(self):
        return self.logger or get_logger()

    def _load_from_module(self, path: str) -> Any:
        module_path, cls = path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        return getattr(module, cls)

    def run(self):
        """
        Generates the converter components from the config and runs the
        transformation
        """
        start_time = datetime.now()
        self.get_logger().info("Starting transformation")

        transformation_configs = self.config.get_transformation_configs()
        if self.config.get("parallel", True):
            threads = list(
                map(
                    lambda c: threading.Thread(
                        target=lambda: self._run_transformation(c)
                    ),
                    transformation_configs,
                )
            )

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()
        else:
            for c in transformation_configs:
                self._run_transformation(c)

        self.get_logger().info(
            f"Transformation finished in {datetime.now() - start_time}"
        )

    def _run_transformation(self, config: TransformationConfig):
        try:
            mapping_class: Type[BaseMapping] = self._load_from_module(
                config.get(
                    "mapping.path", fallback="converter.mapping.FileMapping"
                )
            )
            mapping: BaseMapping = mapping_class(
                config,
                config.file_type,
                **{
                    **config.get("mapping.options", fallback={}),
                    # not loaded from config so it cant be overridden by user input
                    "logger": self.logger,
                    "redact_logs": self.redact_logs,
                }
            )

            extractor_class: Type[BaseConnector] = self._load_from_module(
                config.get(
                    "extractor.path",
                    fallback="converter.connector.CsvConnector",
                )
            )
            extractor: BaseConnector = extractor_class(
                config,
                **{
                    **config.get("extractor.options", fallback={}),
                    # not loaded from config so it cant be overridden by user input
                    "logger": self.logger,
                    "redact_logs": self.redact_logs,
                }
            )

            loader_class: Type[BaseConnector] = self._load_from_module(
                config.get(
                    "loader.path", fallback="converter.connector.CsvConnector"
                )
            )
            loader: BaseConnector = loader_class(
                config,
                **{
                    **config.get("loader.options", fallback={}),
                    # not loaded from config so it cant be overridden by user input
                    "logger": self.logger,
                    "redact_logs": self.redact_logs,
                }
            )

            runner_class: Type[BaseRunner] = self._load_from_module(
                config.get(
                    "runner.path", fallback="converter.runner.PandasRunner"
                )
            )
            runner: BaseRunner = runner_class(
                config,
                **{
                    **config.get("runner.options", fallback={}),
                    # not loaded from config so it cant be overridden by user input
                    "logger": self.logger,
                    "redact_logs": self.redact_logs,
                }
            )

            runner.run(extractor, mapping, loader)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            if exc_tb:
                self.get_logger().error(
                    f"{repr(e)}, line {exc_tb.tb_lineno} in " +
                    f"{exc_tb.tb_frame.f_code.co_filename}\n" +
                    "".join(traceback.format_exception(e))
                )
            else:
                self.get_logger().error(repr(e))

            if self.raise_errors:
                raise
