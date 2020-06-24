from typing import Any, Dict, List

from .base import BaseMapping


class FileMapping(BaseMapping):
    def get_transformations(self) -> Dict[str, List[Any]]:
        return {}
