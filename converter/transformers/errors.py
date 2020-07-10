from converter.errors import ConverterError


class ParserError(ConverterError):
    pass


class UnexpectedCharacters(ParserError):
    def __init__(self, expression, char, position):
        super().__init__(
            f"Unexpected character in {expression}:"
            f" '{char}' at position {position}"
        )
