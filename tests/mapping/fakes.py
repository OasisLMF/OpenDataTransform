from typing import List

from converter.config import Config
from converter.mapping import BaseMapping, MappingSpec
from converter.mapping.base import DirectionalMapping, MappingFormat
from tests.config.fakes import fake_transformation_config


class FakeMapping(BaseMapping):
    def __init__(
        self,
        input_format,
        output_format,
        specs: List[MappingSpec],
        config=None,
    ):
        super().__init__(
            config or fake_transformation_config(),
            "ACC",
            input_format=input_format,
            output_format=output_format,
        )

        self.specs = specs

    @property
    def mapping_specs(self) -> List[MappingSpec]:
        return self.specs


def make_simple_mapping(transformation_set, types=None):
    return FakeMapping(
        MappingFormat(name="A", version="1"),
        MappingFormat(name="B", version="1"),
        [
            MappingSpec(
                "ACC",
                MappingFormat(name="A", version="1"),
                MappingFormat(name="B", version="1"),
                forward=DirectionalMapping(
                    MappingFormat(name="A", version="1"),
                    MappingFormat(name="B", version="1"),
                    transformation_set=transformation_set,
                    types=types or {},
                ),
            )
        ],
    )
