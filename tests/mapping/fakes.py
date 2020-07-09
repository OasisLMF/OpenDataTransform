from typing import List

from converter.config import Config
from converter.mapping import BaseMapping, MappingSpec


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
