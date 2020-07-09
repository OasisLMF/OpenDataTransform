from converter.errors import ConverterError


class NoConversionPathError(ConverterError):
    """
    Error raised there is no valid format map between 2 formats

    :param input_format: The start path in the requested path.
    :param output_format: The end path in the requested path.
    """

    def __init__(self, input_format, output_format):
        self.input_format = input_format
        self.output_format = output_format

        super().__init__(
            f"No conversion path from {input_format} to {output_format}."
        )
