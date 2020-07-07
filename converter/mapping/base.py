from typing import Dict, List, NamedTuple

from converter.config import Config
from converter.config.errors import ConfigurationError


class TransformationEntry(NamedTuple):
    transformation: str
    when: str = "True"


TransformationSet = Dict[str, List[TransformationEntry]]


class BaseMapping:
    """
    Class describing the mapping from the input to the
    output formats.

    :param config: The global config for the system
    :param input_format: The start of the conversion path
    :param output_format: The end of the conversion path
    """

    def __init__(
        self,
        config: Config,
        input_format: str = None,
        output_format: str = None,
        **options
    ):
        self.config = config
        self._options = {
            "input_format": input_format,
            "output_format": output_format,
            **options,
        }

        self.input_format = input_format
        if not self.input_format:
            raise ConfigurationError("input_format not set for the mapping.")

        self.output_format = output_format
        if not self.output_format:
            raise ConfigurationError("output_format not set for the mapping.")

    def get_transformations(self) -> List[TransformationSet]:
        """
        Gets a list of transformation sets to apply to each row.
        Each entry should be allied to each row in order

        :return: The list of transformation sets
        """
        raise NotImplementedError()
