import logging
from datetime import datetime

import yaml

from converter.config import Config
from converter.mapping import BaseMapping


def get_logger():
    return logging.getLogger(__name__)


def log_metadata(config: Config, mapping: BaseMapping):
    get_logger().info(
        yaml.safe_dump(
            {
                "file_type": mapping.file_type,
                "input_format": mapping.input_format._asdict(),
                "output_format": mapping.output_format._asdict(),
                "transformation_path": [
                    {
                        "input_format": edge["spec"].input_format._asdict(),
                        "output_format": edge["spec"].output_format._asdict(),
                        **edge["spec"].metadata,
                    }
                    for edge in mapping.path_edges
                ],
                "data_of_conversion": datetime.now().isoformat(),
                **config.get("metadata", {}),
            }
        )
    )
