from converter.errors import ConverterError


class ParserError(ConverterError):
    """
    Error raised whenever there's an error in the transformation.
    """

    pass


class UnexpectedCharacters(ParserError):
    """
    Error raised when there's an unexpected character in the transformation.
    """

    def __init__(self, expression, char, position):
        super().__init__(
            f"Unexpected character in {expression}:"
            f" '{char}' at position {position}"
        )
