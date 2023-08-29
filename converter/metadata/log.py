import logging
from datetime import datetime

import yaml

from converter.config.config import TransformationConfig
from converter.mapping import BaseMapping


def get_logger():
    return logging.getLogger(__name__)


def log_metadata(
    config: TransformationConfig, mapping: BaseMapping, logger=None
):
    (logger or get_logger()).info(
        yaml.safe_dump(
            [
                {
                    "file_type": mapping.file_type,
                    "input_format": mapping.input_format._asdict(),
                    "output_format": mapping.output_format._asdict(),
                    "transformation_path": [
                        {
                            "input_format": edge[
                                "spec"
                            ].input_format._asdict(),
                            "output_format": edge[
                                "spec"
                            ].output_format._asdict(),
                            **edge["spec"].metadata,
                        }
                        for edge in mapping.path_edges
                    ],
                    # typo fixed below but left original incase
                    # someone is using typo version
                    "data_of_conversion": datetime.now().isoformat(),
                    "date_of_conversion": datetime.now().isoformat(),
                    **config.root_config.get("metadata", {}),
                    **config.get("metadata", {}),
                }
            ]
        )
    )
