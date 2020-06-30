from typing import Dict, List, NamedTuple

from converter.config.errors import ConfigurationError


class TransformationEntry(NamedTuple):
    transformation: str
    when: str = "True"


TransformationSet = Dict[str, List[TransformationEntry]]


class BaseMapping:
    """
    Class describing the mapping from the input to the
    output formats.
    """

    def __init__(self, **options):
        self._options = options

        self.input_format = options.get("input_format")
        if not self.input_format:
            raise ConfigurationError("input_format not set for the mapping.")

        self.output_format = options.get("output_format")
        if not self.output_format:
            raise ConfigurationError("output_format not set for the mapping.")

    def get_transformations(self) -> List[TransformationSet]:
        """
        Gets a list of transformation sets to apply to each row.
        Each entry should be allied to each row in order

        :return: The list of transformation sets
        """
        raise NotImplementedError()
