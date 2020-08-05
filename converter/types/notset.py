class NotSetType:
    """
    Value used when a transformation has not been applied due to  fix
    ambiguity with ``None`` being a valid value
    """

    def __bool__(self):
        return False

    def __eq__(self, other):
        return isinstance(other, NotSetType)


NotSet = NotSetType()
