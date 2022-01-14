import contextlib
from tempfile import NamedTemporaryFile

import yaml

from converter.config.config import (
    Config,
    TransformationConfig,
    deep_merge_dictionary_items,
)


class FakeConfig(Config):
    def __init__(self):
        super().__init__(
            overrides={
                "transformations": {
                    "ACC": {
                        "input_format": {
                            "name": "A",
                            "version": "1",
                        },
                        "output_format": {
                            "name": "B",
                            "version": "1",
                        },
                    }
                }
            }
        )


@contextlib.contextmanager
def config_file(conf):
    with NamedTemporaryFile("w+") as f:
        yaml.safe_dump(
            deep_merge_dictionary_items(
                {
                    "transformations": {
                        "ACC": {
                            "input_format": {
                                "name": "A",
                                "version": "1",
                            },
                            "output_format": {
                                "name": "B",
                                "version": "1",
                            },
                        }
                    }
                },
                conf or {},
            ),
            f,
        )
        yield f.name


def fake_config(conf=None, argv=None, overrides=None, env=None) -> Config:
    with config_file(conf=conf) as p:
        return Config(config_path=p, argv=argv, overrides=overrides, env=env)


def fake_transformation_config(
    conf=None, argv=None, overrides=None, env=None
) -> TransformationConfig:
    return fake_config(
        conf=conf, argv=argv, overrides=overrides, env=env
    ).get_transformation_configs()[0]
