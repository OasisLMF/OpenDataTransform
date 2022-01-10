import logging

import yaml
from datetime import datetime

from converter.config import Config
from converter.mapping import BaseMapping


def get_logger():
    return logging.getLogger(__name__)


def log_metadata(config: Config, mapping: BaseMapping):
    get_logger().info(yaml.dump({
        "input_format": mapping.input_format,
        "output_format": mapping.output_format,
        "transformation_path": [{
            "input_format": edge["spec"].input_format,
            "output_format": edge["spec"].output_format,
            **edge["spec"].metadata,
        } for edge in mapping.path_edges],
        "data_of_conversion": datetime.now().isoformat(),
        **config.get("metadata", {}),
    }))
