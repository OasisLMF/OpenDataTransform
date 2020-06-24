from typing import Any, Dict, List


class BaseMapping:
    """
    Class describing the mapping from the input to the
    output formats.
    """

    def __init__(self, **options):
        self._options = options

    def get_transformations(self) -> Dict[str, List[Any]]:
        """
        Gets a dictionary mapping an output field name to
        a list of transformation objects.

        :return: The transformation dictionary
        """
        raise NotImplementedError()
