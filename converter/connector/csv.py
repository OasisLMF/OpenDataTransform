from typing import Any, Dict, Iterable

from converter.connector.base import BaseConnector


class CsvConnector(BaseConnector):
    def load(self, data: Iterable[Dict[str, Any]]):
        pass

    def extract(self) -> Iterable[Dict[str, Any]]:
        return []
