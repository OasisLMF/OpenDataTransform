from typing import TYPE_CHECKING

from converter.errors import ConverterError


if TYPE_CHECKING:
    from converter.mapping.base import MappingFormat


class NoConversionPathError(ConverterError):
    """
    Error raised there is no valid format map between 2 formats

    :param input_format: The start path in the requested path.
    :param output_format: The end path in the requested path.
    """

    def __init__(
        self, input_format: "MappingFormat", output_format: "MappingFormat"
    ):
        self.input_format = input_format
        self.output_format = output_format

        super().__init__(
            f"No conversion path from {input_format.name} "
            f"v{input_format.version} to {output_format.name} "
            f"v{output_format.version}."
        )
