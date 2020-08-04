from typing import List

from converter.config import Config
from converter.mapping import BaseMapping, MappingSpec
from converter.mapping.base import DirectionalMapping


class FakeMapping(BaseMapping):
    def __init__(
        self,
        input_format,
        output_format,
        specs: List[MappingSpec],
        config=None,
    ):
        super().__init__(
            config or Config(),
            input_format=input_format,
            output_format=output_format,
        )

        self.specs = specs

    @property
    def mapping_specs(self) -> List[MappingSpec]:
        return self.specs


def make_simple_mapping(transformation_set):
    return FakeMapping(
        "A",
        "B",
        [
            MappingSpec(
                "A",
                "B",
                forward=DirectionalMapping(
                    "A", "B", transformation_set=transformation_set
                ),
            )
        ],
    )
